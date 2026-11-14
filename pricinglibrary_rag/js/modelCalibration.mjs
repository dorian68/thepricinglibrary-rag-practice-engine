/**
 * Deterministic, dependency-free volatility calibration engine.
 *
 * Conventions:
 * - strikes and forwards use the same units;
 * - when `forward` is omitted, strikes are interpreted as forward moneyness
 *   against F=1;
 * - rates and discounting are zero/one (forward measure);
 * - volatilities are decimals (0.20 = 20%).
 */

export const MODEL_CALIBRATION_VERSION = '1.0.0';
export const MAX_SURFACE_POINTS = 250;

const EPSILON = 1e-12;
const DEFAULT_FORWARD = 1;

const MODEL_BOUNDS = Object.freeze({
  black: Object.freeze({ sigma: [0.01, 2] }),
  sabr: Object.freeze({
    alpha: [0.01, 1.5],
    beta: [0.05, 1],
    rho: [-0.95, 0.95],
    nu: [0.01, 3],
  }),
  heston: Object.freeze({
    v0: [0.0025, 0.64],
    kappa: [0.05, 12],
    theta: [0.0025, 0.64],
    sigma: [0.02, 3],
    rho: [-0.95, 0.95],
  }),
});

const clamp = (value, lower, upper) => Math.min(upper, Math.max(lower, value));

const mean = (values) => values.reduce((total, value) => total + value, 0) / values.length;

const weightedMean = (values, weights) => {
  const totalWeight = weights.reduce((total, weight) => total + weight, 0);
  return values.reduce((total, value, index) => total + value * weights[index], 0) / totalWeight;
};

const normalCdf = (x) => {
  const sign = x < 0 ? -1 : 1;
  const value = Math.abs(x) / Math.sqrt(2);
  const t = 1 / (1 + 0.3275911 * value);
  const polynomial = (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t;
  const erf = sign * (1 - polynomial * Math.exp(-value * value));
  return 0.5 * (1 + erf);
};

export const black76Call = (forward, strike, maturity, volatility) => {
  if (![forward, strike, maturity, volatility].every(Number.isFinite)) {
    throw new Error('Black inputs must be finite numbers.');
  }
  if (forward <= 0 || strike <= 0 || maturity <= 0 || volatility < 0) {
    throw new Error('Black requires forward, strike and maturity > 0 and volatility >= 0.');
  }
  if (volatility <= EPSILON) return Math.max(forward - strike, 0);
  const standardDeviation = volatility * Math.sqrt(maturity);
  const d1 = Math.log(forward / strike) / standardDeviation + 0.5 * standardDeviation;
  const d2 = d1 - standardDeviation;
  return forward * normalCdf(d1) - strike * normalCdf(d2);
};

export const impliedBlackVolatility = (price, forward, strike, maturity) => {
  if (![price, forward, strike, maturity].every(Number.isFinite)) return Number.NaN;
  const intrinsic = Math.max(forward - strike, 0);
  const upper = forward;
  if (price < intrinsic - 1e-10 || price > upper + 1e-10 || forward <= 0 || strike <= 0 || maturity <= 0) {
    return Number.NaN;
  }
  if (price <= intrinsic + 1e-10) return 0;
  let low = 1e-7;
  let high = 5;
  for (let iteration = 0; iteration < 72; iteration += 1) {
    const mid = 0.5 * (low + high);
    const candidate = black76Call(forward, strike, maturity, mid);
    if (candidate > price) high = mid;
    else low = mid;
  }
  return 0.5 * (low + high);
};

export const sabrHaganLognormalVolatility = (forward, strike, maturity, parameters) => {
  const { alpha, beta, rho, nu } = parameters;
  if (![forward, strike, maturity, alpha, beta, rho, nu].every(Number.isFinite)) return Number.NaN;
  if (forward <= 0 || strike <= 0 || maturity <= 0 || alpha <= 0 || beta < 0 || beta > 1 || Math.abs(rho) >= 1 || nu <= 0) {
    return Number.NaN;
  }

  const oneMinusBeta = 1 - beta;
  const logForwardStrike = Math.log(forward / strike);
  const forwardStrike = forward * strike;
  const forwardStrikePower = Math.pow(forwardStrike, 0.5 * oneMinusBeta);
  const alphaScale = alpha / Math.max(forwardStrikePower, EPSILON);
  const correction = (
    (oneMinusBeta * oneMinusBeta * alpha * alpha) / (24 * Math.pow(forwardStrike, oneMinusBeta))
    + (rho * beta * nu * alpha) / (4 * Math.max(forwardStrikePower, EPSILON))
    + ((2 - 3 * rho * rho) * nu * nu) / 24
  ) * maturity;

  if (Math.abs(logForwardStrike) < 1e-8) {
    return (alpha / Math.pow(forward, oneMinusBeta)) * (1 + correction);
  }

  const z = (nu / alpha) * forwardStrikePower * logForwardStrike;
  const squareRoot = Math.sqrt(Math.max(1 - 2 * rho * z + z * z, EPSILON));
  const xOfZ = Math.log((squareRoot + z - rho) / (1 - rho));
  const zOverX = Math.abs(xOfZ) < 1e-10 ? 1 : z / xOfZ;
  const logSquared = logForwardStrike * logForwardStrike;
  const denominator = forwardStrikePower * (
    1 + (oneMinusBeta * oneMinusBeta * logSquared) / 24
      + (Math.pow(oneMinusBeta, 4) * logSquared * logSquared) / 1920
  );
  const result = (alpha / denominator) * zOverX * (1 + correction);
  return result > 0 && Number.isFinite(result) ? result : Number.NaN;
};

// Minimal complex arithmetic for the Heston characteristic function.
const complex = (re, im = 0) => ({ re, im });
const cAdd = (left, right) => complex(left.re + right.re, left.im + right.im);
const cSub = (left, right) => complex(left.re - right.re, left.im - right.im);
const cScale = (value, scalar) => complex(value.re * scalar, value.im * scalar);
const cMul = (left, right) => complex(left.re * right.re - left.im * right.im, left.re * right.im + left.im * right.re);
const cDiv = (left, right) => {
  const denominator = right.re * right.re + right.im * right.im;
  if (denominator < 1e-28) return complex(Number.NaN, Number.NaN);
  return complex(
    (left.re * right.re + left.im * right.im) / denominator,
    (left.im * right.re - left.re * right.im) / denominator,
  );
};
const cExp = (value) => {
  const magnitude = Math.exp(value.re);
  return complex(magnitude * Math.cos(value.im), magnitude * Math.sin(value.im));
};
const cLog = (value) => complex(Math.log(Math.hypot(value.re, value.im)), Math.atan2(value.im, value.re));
const cSqrt = (value) => {
  const magnitude = Math.hypot(value.re, value.im);
  const re = Math.sqrt(Math.max(0, 0.5 * (magnitude + value.re)));
  const imMagnitude = Math.sqrt(Math.max(0, 0.5 * (magnitude - value.re)));
  return complex(re, value.im < 0 ? -imMagnitude : imMagnitude);
};

const hestonCharacteristic = (argument, maturity, parameters, logForward = 0) => {
  const { v0, kappa, theta, sigma, rho } = parameters;
  const iU = complex(-argument.im, argument.re);
  const uSquared = cMul(argument, argument);
  const b = cSub(complex(kappa), cScale(iU, rho * sigma));
  const discriminant = cAdd(cMul(b, b), cScale(cAdd(uSquared, iU), sigma * sigma));
  const d = cSqrt(discriminant);
  const bMinusD = cSub(b, d);
  const bPlusD = cAdd(b, d);
  const g = cDiv(bMinusD, bPlusD);
  const expMinusDT = cExp(cScale(d, -maturity));
  const one = complex(1);
  const oneMinusGExp = cSub(one, cMul(g, expMinusDT));
  const oneMinusG = cSub(one, g);
  const logarithm = cLog(cDiv(oneMinusGExp, oneMinusG));
  const cTerm = cScale(
    cSub(cScale(bMinusD, maturity), cScale(logarithm, 2)),
    (kappa * theta) / (sigma * sigma),
  );
  const dTerm = cScale(
    cMul(bMinusD, cDiv(cSub(one, expMinusDT), oneMinusGExp)),
    1 / (sigma * sigma),
  );
  return cExp(cAdd(cAdd(cScale(iU, logForward), cTerm), cScale(dTerm, v0)));
};

const simpsonIntegral = (integrand, lower, upper, intervals) => {
  const count = intervals % 2 === 0 ? intervals : intervals + 1;
  const width = (upper - lower) / count;
  let total = integrand(lower) + integrand(upper);
  for (let index = 1; index < count; index += 1) {
    total += (index % 2 === 0 ? 2 : 4) * integrand(lower + index * width);
  }
  return total * width / 3;
};

export const hestonForwardCall = (forward, strike, maturity, parameters, integration = {}) => {
  const { v0, kappa, theta, sigma, rho } = parameters;
  if (![forward, strike, maturity, v0, kappa, theta, sigma, rho].every(Number.isFinite)) return Number.NaN;
  if (forward <= 0 || strike <= 0 || maturity <= 0 || v0 <= 0 || kappa <= 0 || theta <= 0 || sigma <= 0 || Math.abs(rho) >= 1) {
    return Number.NaN;
  }

  const upper = integration.upper ?? 80;
  const intervals = integration.intervals ?? 64;
  const lower = 1e-5;
  const logStrike = Math.log(strike);
  const logForward = Math.log(forward);
  const phiMinusI = hestonCharacteristic(complex(0, -1), maturity, parameters, logForward);

  const probability = (kind) => {
    const integrand = (u) => {
      const shiftedArgument = kind === 1 ? complex(u, -1) : complex(u, 0);
      const phi = hestonCharacteristic(shiftedArgument, maturity, parameters, logForward);
      const phase = complex(Math.cos(-u * logStrike), Math.sin(-u * logStrike));
      const numerator = cMul(phase, phi);
      const denominator = kind === 1
        ? cMul(complex(0, u), phiMinusI)
        : complex(0, u);
      return cDiv(numerator, denominator).re;
    };
    return clamp(0.5 + simpsonIntegral(integrand, lower, upper, intervals) / Math.PI, 0, 1);
  };

  const call = forward * probability(1) - strike * probability(2);
  return clamp(call, Math.max(forward - strike, 0), forward);
};

const normalizeHeader = (header) => header.trim().toLowerCase().replace(/[\s_\-()%]/g, '');

const splitCsvLine = (line, delimiter) => {
  const values = [];
  let current = '';
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (character === '"') {
      if (quoted && line[index + 1] === '"') {
        current += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (character === delimiter && !quoted) {
      values.push(current.trim());
      current = '';
    } else {
      current += character;
    }
  }
  if (quoted) throw new Error('CSV contains an unterminated quoted field.');
  values.push(current.trim());
  return values;
};

const HEADER_ALIASES = Object.freeze({
  strike: ['strike', 'k', 'moneyness', 'strikeforward'],
  maturity: ['maturity', 'tenor', 't', 'yearstomaturity', 'expiry'],
  impliedVol: ['impliedvol', 'impliedvolatility', 'iv', 'vol', 'volatility'],
  forward: ['forward', 'f', 'forwardprice'],
  weight: ['weight', 'w'],
});

const findHeaderIndex = (headers, field, required) => {
  const aliases = HEADER_ALIASES[field];
  const index = headers.findIndex((header) => aliases.includes(header));
  if (required && index < 0) {
    throw new Error(`CSV is missing required column '${field}'.`);
  }
  return index;
};

export const parseVolatilitySurfaceCsv = (text) => {
  if (typeof text !== 'string' || !text.trim()) throw new Error('CSV file is empty.');
  const lines = text.replace(/^\uFEFF/, '').split(/\r?\n/).filter((line) => line.trim() && !line.trim().startsWith('#'));
  if (lines.length < 2) throw new Error('CSV must contain a header and at least one data row.');
  const delimiterCandidates = [',', ';', '\t'];
  const delimiter = delimiterCandidates
    .map((candidate) => ({ candidate, count: splitCsvLine(lines[0], candidate).length }))
    .sort((left, right) => right.count - left.count)[0].candidate;
  const headers = splitCsvLine(lines[0], delimiter).map(normalizeHeader);
  const indices = {
    strike: findHeaderIndex(headers, 'strike', true),
    maturity: findHeaderIndex(headers, 'maturity', true),
    impliedVol: findHeaderIndex(headers, 'impliedVol', true),
    forward: findHeaderIndex(headers, 'forward', false),
    weight: findHeaderIndex(headers, 'weight', false),
  };

  const surface = [];
  const seen = new Set();
  for (let row = 1; row < lines.length; row += 1) {
    const values = splitCsvLine(lines[row], delimiter);
    const parseCell = (index, fallback) => index < 0 || values[index] === undefined || values[index] === '' ? fallback : Number(values[index].replace(',', '.'));
    const point = {
      strike: parseCell(indices.strike, Number.NaN),
      maturity: parseCell(indices.maturity, Number.NaN),
      impliedVol: parseCell(indices.impliedVol, Number.NaN),
      forward: parseCell(indices.forward, DEFAULT_FORWARD),
      weight: parseCell(indices.weight, 1),
    };
    try {
      validatePoint(point, `CSV row ${row + 1}`);
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : String(error));
    }
    const key = `${point.strike}|${point.maturity}|${point.forward}`;
    if (seen.has(key)) throw new Error(`CSV row ${row + 1} duplicates strike/maturity/forward ${key}.`);
    seen.add(key);
    surface.push(point);
  }
  validateSurface(surface);
  return surface;
};

const validatePoint = (point, label = 'Surface point') => {
  const values = [point.strike, point.maturity, point.impliedVol, point.forward ?? DEFAULT_FORWARD, point.weight ?? 1];
  if (!values.every(Number.isFinite)) throw new Error(`${label} contains a non-finite value.`);
  if (point.strike <= 0) throw new Error(`${label}: strike must be > 0.`);
  if (point.maturity <= 0 || point.maturity > 50) throw new Error(`${label}: maturity must be in (0, 50] years.`);
  if (point.impliedVol <= 0 || point.impliedVol > 5) throw new Error(`${label}: implied volatility must be in (0, 5].`);
  if ((point.forward ?? DEFAULT_FORWARD) <= 0) throw new Error(`${label}: forward must be > 0.`);
  if ((point.weight ?? 1) <= 0) throw new Error(`${label}: weight must be > 0.`);
};

export const validateSurface = (surface) => {
  if (!Array.isArray(surface) || surface.length < 5) throw new Error('Calibration requires at least five valid surface points.');
  if (surface.length > MAX_SURFACE_POINTS) throw new Error(`Calibration accepts at most ${MAX_SURFACE_POINTS} surface points per run.`);
  surface.forEach((point, index) => validatePoint(point, `Surface point ${index + 1}`));
  const strikes = new Set(surface.map((point) => point.strike));
  const maturities = new Set(surface.map((point) => point.maturity));
  if (strikes.size < 3) throw new Error('Calibration requires at least three distinct strikes.');
  if (maturities.size < 1) throw new Error('Calibration requires at least one maturity.');
  return true;
};

export const generateSyntheticVolatilitySurface = () => {
  const strikes = [0.8, 0.85, 0.9, 0.95, 1, 1.05, 1.1, 1.15, 1.2];
  const maturities = [0.1, 0.25, 0.5, 1, 2];
  const parameters = { alpha: 0.2, beta: 0.72, rho: -0.28, nu: 0.48 };
  return maturities.flatMap((maturity) => strikes.map((strike) => ({
    strike,
    maturity,
    forward: 1,
    weight: 1,
    impliedVol: sabrHaganLognormalVolatility(1, strike, maturity, parameters),
  })));
};

const modelVolatility = (model, point, parameters, integration) => {
  const forward = point.forward ?? DEFAULT_FORWARD;
  if (model === 'black') return parameters.sigma;
  if (model === 'sabr') return sabrHaganLognormalVolatility(forward, point.strike, point.maturity, parameters);
  if (model === 'heston') {
    const price = hestonForwardCall(forward, point.strike, point.maturity, parameters, integration);
    return impliedBlackVolatility(price, forward, point.strike, point.maturity);
  }
  return Number.NaN;
};

const parameterObjectFromVector = (keys, vector) => Object.fromEntries(keys.map((key, index) => [key, vector[index]]));

const boundedPatternSearch = ({ keys, bounds, starts, objective, maxIterations, tolerance }) => {
  let best = null;
  let evaluations = 0;
  for (const start of starts) {
    let vector = keys.map((key, index) => clamp(start[index], bounds[key][0], bounds[key][1]));
    let steps = keys.map((key) => 0.18 * (bounds[key][1] - bounds[key][0]));
    let score = objective(parameterObjectFromVector(keys, vector));
    evaluations += 1;
    let iterationsUsed = 0;
    let converged = false;
    for (let iteration = 0; iteration < maxIterations; iteration += 1) {
      iterationsUsed = iteration + 1;
      let improved = false;
      for (let dimension = 0; dimension < keys.length; dimension += 1) {
        let dimensionBest = score;
        let dimensionVector = vector;
        for (const direction of [-1, 1]) {
          const candidate = [...vector];
          candidate[dimension] = clamp(
            candidate[dimension] + direction * steps[dimension],
            bounds[keys[dimension]][0],
            bounds[keys[dimension]][1],
          );
          if (candidate[dimension] === vector[dimension]) continue;
          const candidateScore = objective(parameterObjectFromVector(keys, candidate));
          evaluations += 1;
          if (candidateScore + 1e-14 < dimensionBest) {
            dimensionBest = candidateScore;
            dimensionVector = candidate;
          }
        }
        if (dimensionBest + 1e-14 < score) {
          vector = dimensionVector;
          score = dimensionBest;
          improved = true;
        }
      }
      if (!improved) steps = steps.map((step) => step * 0.5);
      const normalizedStep = Math.max(...steps.map((step, index) => step / (bounds[keys[index]][1] - bounds[keys[index]][0])));
      if (normalizedStep < tolerance) {
        converged = true;
        break;
      }
    }
    const candidate = { parameters: parameterObjectFromVector(keys, vector), score, iterations: iterationsUsed, converged };
    if (!best || candidate.score < best.score) best = candidate;
  }
  return { ...best, evaluations };
};

const initialCandidates = (model, surface) => {
  const vols = surface.map((point) => point.impliedVol);
  const weights = surface.map((point) => point.weight ?? 1);
  const atmPoints = surface.filter((point) => Math.abs(point.strike / (point.forward ?? DEFAULT_FORWARD) - 1) < 0.03);
  const atmVol = atmPoints.length ? mean(atmPoints.map((point) => point.impliedVol)) : weightedMean(vols, weights);
  if (model === 'black') return [[atmVol]];
  if (model === 'sabr') {
    return [
      [atmVol, 0.7, -0.2, 0.45],
      [atmVol, 0.95, -0.45, 0.8],
      [atmVol, 0.4, 0.1, 0.25],
    ];
  }
  const shortPoints = [...surface].sort((left, right) => left.maturity - right.maturity).slice(0, Math.max(3, Math.floor(surface.length / 5)));
  const longPoints = [...surface].sort((left, right) => right.maturity - left.maturity).slice(0, Math.max(3, Math.floor(surface.length / 5)));
  const shortVariance = Math.pow(mean(shortPoints.map((point) => point.impliedVol)), 2);
  const longVariance = Math.pow(mean(longPoints.map((point) => point.impliedVol)), 2);
  return [
    [shortVariance, 1.5, longVariance, 0.45, -0.35],
    [shortVariance, 3, longVariance, 0.8, -0.65],
  ];
};

const buildDiagnostics = (surface, calibratedSurface, search, objectiveName, model, parameters) => {
  const weights = surface.map((point) => point.weight ?? 1);
  const totalWeight = weights.reduce((total, weight) => total + weight, 0);
  const weightedSquaredErrors = calibratedSurface.map((point, index) => weights[index] * point.signedError * point.signedError);
  const rmse = Math.sqrt(weightedSquaredErrors.reduce((total, value) => total + value, 0) / totalWeight);
  const priceRmse = Math.sqrt(calibratedSurface.reduce((total, point, index) => total + weights[index] * point.priceError * point.priceError, 0) / totalWeight);
  const marketMean = weightedMean(surface.map((point) => point.impliedVol), weights);
  const totalVariance = surface.reduce((total, point, index) => total + weights[index] * Math.pow(point.impliedVol - marketMean, 2), 0);
  const residualVariance = weightedSquaredErrors.reduce((total, value) => total + value, 0);
  const warnings = [];
  if (!search.converged) warnings.push('Optimizer stopped at its iteration budget; treat this as a candidate fit, not a unique optimum.');
  if (model === 'sabr') warnings.push('SABR uses the Hagan lognormal asymptotic approximation under the forward measure.');
  if (model === 'heston') {
    const feller = 2 * parameters.kappa * parameters.theta - parameters.sigma * parameters.sigma;
    if (feller < 0) warnings.push('Feller condition is not satisfied; variance can reach zero under this parameter set.');
    warnings.push('Heston prices use deterministic Fourier integration; validate production trades with an independent library and market conventions.');
  }
  return {
    rmse,
    priceRmse,
    meanAbsoluteError: weightedMean(calibratedSurface.map((point) => point.error), weights),
    maxAbsoluteError: Math.max(...calibratedSurface.map((point) => point.error)),
    rSquared: totalVariance <= EPSILON ? null : 1 - residualVariance / totalVariance,
    points: surface.length,
    iterations: search.iterations,
    evaluations: search.evaluations,
    converged: search.converged,
    objective: objectiveName,
    fellerMargin: model === 'heston' ? 2 * parameters.kappa * parameters.theta - parameters.sigma * parameters.sigma : null,
    warnings,
  };
};

export const calibrateVolatilityModel = (model, rawSurface, options = {}) => {
  if (!Object.hasOwn(MODEL_BOUNDS, model)) throw new Error(`Unsupported model '${model}'.`);
  validateSurface(rawSurface);
  const surface = rawSurface.map((point) => ({
    strike: Number(point.strike),
    maturity: Number(point.maturity),
    impliedVol: Number(point.impliedVol),
    forward: point.forward === undefined ? DEFAULT_FORWARD : Number(point.forward),
    weight: point.weight === undefined ? 1 : Number(point.weight),
  }));
  const objectiveName = options.objective === 'price' ? 'price' : 'volatility';
  const bounds = MODEL_BOUNDS[model];
  const keys = Object.keys(bounds);
  const integration = {
    upper: options.integrationUpper ?? 80,
    intervals: options.integrationIntervals ?? 64,
  };
  const objective = (parameters) => {
    let total = 0;
    let totalWeight = 0;
    for (const point of surface) {
      const modelVol = modelVolatility(model, point, parameters, integration);
      if (!Number.isFinite(modelVol) || modelVol <= 0 || modelVol > 5) return 1e6;
      const forward = point.forward ?? DEFAULT_FORWARD;
      const modelPrice = black76Call(forward, point.strike, point.maturity, modelVol);
      const marketPrice = black76Call(forward, point.strike, point.maturity, point.impliedVol);
      const error = objectiveName === 'price' ? modelPrice - marketPrice : modelVol - point.impliedVol;
      total += point.weight * error * error;
      totalWeight += point.weight;
    }
    return Math.sqrt(total / totalWeight);
  };

  const search = boundedPatternSearch({
    keys,
    bounds,
    starts: initialCandidates(model, surface),
    objective,
    maxIterations: options.maxIterations ?? (model === 'heston' ? 70 : model === 'sabr' ? 90 : 45),
    tolerance: options.tolerance ?? (model === 'heston' ? 0.003 : 0.00025),
  });
  if (!search || !Number.isFinite(search.score) || search.score >= 1e5) {
    throw new Error(`${model.toUpperCase()} calibration failed to find a finite solution.`);
  }

  const calibratedSurface = surface.map((point) => {
    const modelVol = modelVolatility(model, point, search.parameters, integration);
    const forward = point.forward ?? DEFAULT_FORWARD;
    const marketPrice = black76Call(forward, point.strike, point.maturity, point.impliedVol);
    const modelPrice = black76Call(forward, point.strike, point.maturity, modelVol);
    const signedError = modelVol - point.impliedVol;
    return {
      ...point,
      modelVol,
      signedError,
      error: Math.abs(signedError),
      marketPrice,
      modelPrice,
      priceError: modelPrice - marketPrice,
    };
  });
  const diagnostics = buildDiagnostics(surface, calibratedSurface, search, objectiveName, model, search.parameters);
  return {
    model,
    version: MODEL_CALIBRATION_VERSION,
    assumptions: {
      measure: 'forward',
      discountFactor: 1,
      defaultForward: DEFAULT_FORWARD,
      volatilityUnit: 'decimal',
    },
    parameters: search.parameters,
    parameterBounds: bounds,
    calibratedSurface,
    diagnostics,
    rmse: diagnostics.rmse,
  };
};
