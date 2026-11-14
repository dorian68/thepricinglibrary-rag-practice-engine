"""Authored explanations for each wrong option in the English course quizzes.

Each tuple follows the four distractors in Course.quiz; display positions may
rotate, but an explanation always stays attached to its actual option. There
is deliberately no lexical classifier or generic feedback fallback.
"""

FEEDBACK = {
    "vanilla_bs": (
        (
            "The buyer's physical return forecast is not an input to this replication price. Under the stated model, carry sets the pricing-measure drift.",
            "A probability of profit depends on premium and the physical distribution. It is not the risk-neutral carry convention used to value the contractual payoff.",
            "A dealer's target investment return does not replace the model's funding and dividend assumptions. Commercial pricing decisions are separate from clean replication value.",
            "Ideal continuous replication has explicit assumptions. Discrete execution, jumps, costs and model error can produce hedging losses.",
        ),
        (
            "Buying underlying adds positive delta to an already positive signed book. Selling the corresponding exposure is the local offset.",
            "Selling volatility primarily changes vega and other option risks. A currency amount of volatility exposure is not the same coordinate as underlying delta.",
            "Contract multiplier converts unit option delta into actual shares or exposure. Omitting it can create a factor-of-a-hundred hedge error.",
            "An underlying hedge is linear. It offsets initial delta while option convexity and discontinuous market moves remain exposed.",
        ),
        (
            "Parity matches terminal cash flows under a consistent carry framework. It cannot determine the stock's future realised path volatility.",
            "The replication identity does not infer a physical exercise probability. Cash-flow equivalence and probability forecasting are different questions.",
            "One matched call-put pair does not test all strike convexity or calendar relationships. Surface-wide static-arbitrage checks remain necessary.",
            "European parity does not determine an American option's early-exercise premium. Exercise flexibility requires separate bounds or an American valuation model.",
        ),
        (
            "One volatility percentage point is 0.01 in decimal volatility. Multiplying decimal vega by 100 moves in the opposite direction and creates a unit error.",
            "Gamma is spot curvature, not the derivative with respect to volatility. Multiplying it by spot cannot supply the required vega conversion.",
            "A premium is a currency price, while the shock here is a change in volatility. Substituting premium mixes unrelated units.",
            "A change of one full decimal volatility is one hundred volatility points. It is not the one-point shock in the question.",
        ),
        (
            "Setting dividends to zero changes carry and the reference price. An unconfirmed input must be disclosed as an assumption, not silently treated as observed.",
            "Historical realised volatility is a different quantity. Replacing the quoting input does not resolve the missing dividend assumption.",
            "More displayed precision only rounds the same conditional calculation more finely. It supplies no evidence about the dividend input.",
            "A clean conditional model value omits execution, spread and other commercial considerations. Unconfirmed carry prevents presenting it as an unconditional executable bid.",
        ),
    ),
    "greeks": (
        (
            "The second-order Taylor contribution uses the squared shock, not an unsquared decimal return. Its risk coordinate must match the quoted gamma units.",
            "Squaring a shock preserves its magnitude but removes its direction. Using only a sign loses the quadratic scale of the curvature contribution.",
            "The Taylor coefficient is one half of the second derivative. Multiplying by twice gamma overstates that contribution by a factor of four.",
            "For this gamma convention, a short-gamma position has a negative curvature contribution for either shock direction. Other P&L components can still offset it.",
        ),
        (
            "Initial delta neutrality is a local first-order condition. As spot moves, gamma changes the delta and creates a need to rebalance.",
            "Gamma, vega, theta, jumps and trading costs can contribute after delta is neutralised. A zero initial slope does not fix realised P&L.",
            "An option book still has nonlinear and other factor exposures. Removing delta does not transform it into a risk-free cash deposit.",
            "A position in the underlying has no option gamma. It changes the linear exposure without reversing the book's curvature.",
        ),
        (
            "Opposite maturity vegas cancel only for the specified common shift. A term-structure twist can move their volatility inputs differently.",
            "A short-dated event can affect one bucket much more than another. The net parallel vega hides, rather than rules out, that concentration.",
            "Risk netting does not execute the trades. Each position may still have its own bid-offer spread and unwind liquidity.",
            "Sticky-strike and sticky-delta conventions can imply different effective risks. Netting maturity vegas does not make those dynamics identical.",
        ),
        (
            "Forcing the residual into a Greek creates a balancing entry without an economic explanation. Preserve the discrepancy and investigate its cause.",
            "Closing risks describe a different market state and possibly a different book. Replacing opening risks destroys the original explain basis.",
            "Intraday hedge trades change exposure and cash flows. Omitting them leaves actual P&L incomparable with the opening-book factor explain.",
            "A residual can arise from booking, data, conventions or higher-order terms. It is not evidence of trading skill until those mechanisms are reconciled.",
        ),
        (
            "Call versus put does not determine the clock used by the risk system. Calendar-day and trading-day theta require different elapsed-time inputs.",
            "Display colour contains no time or carry convention. The calculation needs the theta definition and actual explain interval.",
            "Portfolio sign and contract features prevent a universal theta rule. Even a negative theta still needs the correct time unit.",
            "Volatility points apply to vega. Theta multiplies elapsed time, so a volatility conversion cannot replace the calendar/trading-day convention.",
        ),
    ),
    "swap": (
        (
            "Positive notional sets scale, not value sign. A fixed payer paying above the current par coupon has negative local value under the stated convention.",
            "A standard same-currency swap exchanges interest cash flows, not the entire notional as the swap's inception price. Principal is only the scaling base here.",
            "The existing contractual coupon remains fixed. Today's par rate changes its mark-to-market rather than resetting the old coupon to zero value.",
            "Reversing payer and receiver reverses the signed net cash flows and PV. Position side cannot be omitted from this valuation.",
        ),
        (
            "The annuity is a present-value-weighted accrual factor, not the swap principal. Notional and a coupon difference are still needed to obtain currency PV.",
            "With accruals measured in years, the annuity has year units. Multiplying by notional and 0.0001 gives the DV01 magnitude in currency per basis point.",
            "The coupon difference is applied after constructing the annuity. Including it inside the annuity would conflate a schedule weight with the signed swap value.",
            "Discount factors change under a curve shock, so the annuity can change. Freezing it is the explicitly local approximation in the worked ticket.",
        ),
        (
            "A steepener or flattener moves tenor buckets differently. Equal parallel totals can leave substantial nonparallel exposure.",
            "Forecast-versus-discount basis can move independently of the parallel rate scenario. Matching one DV01 does not remove that curve-basis mechanism.",
            "Different cash-flow schedules and calibration mappings create different node risks. Equality of their sums does not imply equality of every bucket.",
            "Schedules locate the cash flows that generate risk. Discarding them prevents checking maturity exposure, fixings and hedge compatibility.",
        ),
        (
            "A realised contractual fixing is historical information and does not become today's par swap rate. Only unfixed coupons are projected anew.",
            "A floating coupon remains an interest payment. A market move does not transform it into a notional principal exchange.",
            "Today's curve cannot rewrite the actual past fixing. Keep fixing history separate from current projection and discounting inputs.",
            "Changing market rates does not create a new contractual accrual period. The existing schedule determines the dates and payment entitlement.",
        ),
        (
            "Negative par rates can be economically coherent. Check schedules, discount factors, collateral conventions and instrument repricing before asserting arbitrage.",
            "An inverted term structure can reflect genuine market pricing. Its slope alone does not establish an interpolation defect.",
            "Negative rates can imply positive discount factors above one. Positivity and coherent pricing matter; a universal below-one rule is invalid.",
            "Deleting a negative quote discards information without diagnosing it. Retain the observation and investigate its source and conventions.",
        ),
    ),
    "yield_curve": (
        (
            "A zero rate is defined through discounting a single terminal payment. It does not exclude discounting; it is a compounding representation of it.",
            "A quoted par rate is a present valuation quantity. It is not the realised future overnight rate or a guarantee of that future fixing.",
            "Coupon cash flows at earlier dates enter the par equation. Single-curve consistency does not make that rate identical to the terminal zero rate.",
            "A par/zero difference can follow solely from coupon timing and compounding. Negative-rate arbitrage is not implied by that ordinary difference.",
        ),
        (
            "One terminal par quote does not identify both discount factors in an intermediate interval. Earlier calibration and construction rules are needed.",
            "A chart's colour is a display choice. The forward comes from a discount-factor ratio and a specified interval convention.",
            "Positive rates do not uniquely determine a forward, and rates need not always be positive. The actual discount weights and conventions are required.",
            "Historical returns are not a replacement for the calibrated discount-factor ratio. This forward is a valuation quantity under the stated curve framework.",
        ),
        (
            "Unquoted maturities are governed by interpolation or extrapolation assumptions. Pillar fit does not independently validate those regions.",
            "A fitted curve encodes market-implied pricing relationships. It does not establish an unbiased physical forecast of future realised rates.",
            "Calibration and validation can share the same schedule error and still match. An independent calendar/convention check is necessary.",
            "Several interpolation rules can fit the same pillars while producing different forwards and risks. Calibration fit does not remove that model choice.",
        ),
        (
            "A non-finite discount factor cannot provide a well-defined payment PV. Reject or diagnose it rather than treating it as an ordinary curve state.",
            "A residual far beyond quote precision means the calibration/control does not reproduce its target. It requires investigation even if the curve looks smooth.",
            "Mixing decimal and percentage rates changes the economic inputs, often by a factor of one hundred. That is a unit error, not a legitimate curve shape.",
            "Forecast and collateral discount curves serve different cash-flow roles. Using one for the other needs an explicit justified single-curve assumption.",
        ),
        (
            "A par quote maps through calibration into discount factors at several dates. A zero-node bump is a different coordinate and produces different risks.",
            "Rebuilding enforces the declared calibration, not universal positivity. Valid market rates can remain negative after a consistent rebuild.",
            "Earlier coupons and shared calibration/interpolation can propagate the quote change across several dates. Only-final-payment behaviour is not general.",
            "Intermediate target cash flows are discounted using the constructed curve. Their value and sensitivity can depend materially on interpolation.",
        ),
    ),
    "bond": (
        (
            "Nominal is the principal basis, whereas duration scales proportional price change. A premium or discount price makes market value differ from nominal.",
            "Accrued interest is only one component of dirty settlement value. It is not the complete market exposure whose yield sensitivity is measured.",
            "A coupon rate is dimensionless per year, not the bond's current currency value. It cannot replace market value in a currency DV01.",
            "Counting payment dates ignores their discounted cash weights. Duration and market value depend on amounts and timing, not an unweighted count.",
        ),
        (
            "Positive convexity contributes a positive squared-shock term. For a yield rise it offsets part of the duration loss, so duration-only overstates that loss locally.",
            "Duration is a first derivative and the finite-shock expression omits higher orders. Even adding convexity does not generally give exact repricing.",
            "An ordinary positive-cash-flow option-free bond has positive price-yield convexity. Negative convexity requires another mechanism, such as embedded optionality in relevant states.",
            "A yield move must still be converted from basis points into a decimal. Correct curvature does not repair an incorrect shock unit.",
        ),
        (
            "A clean quote excludes accrued interest and is usually per 100 nominal. Settlement cash needs dirty price and the notional scaling.",
            "Coupon frequency changes the accrual calculation but does not justify adding the same accrued amount twice. Apply the schedule and day count once.",
            "Dirty value includes the present value of the remaining contractual cash flows. Coupon entitlement is handled by settlement conventions, not excluded universally.",
            "A per-100 price is a unit quote. Multiply dirty price by nominal divided by 100 to obtain the full settlement cash amount.",
        ),
        (
            "A holding-period return depends on reinvestment, sale price, credit and costs. YTM is a pricing rate, not a guarantee of that realised outcome.",
            "A promised-cash-flow yield equation does not model default timing or recovery. Credit-adjusted valuation requires additional assumptions and instruments.",
            "Settlement determines remaining payments and accrued interest; coupon timing determines discount exponents. Both affect the solved yield.",
            "A single bond yield summarises multiple cash flows. A zero curve assigns maturity-specific discounting, so the quantities are not generally identical.",
        ),
        (
            "A rates-duration match targets one local coordinate. It cannot eliminate all losses from spread moves, default, liquidity or nonlinear response.",
            "Trading a government bond does not change the corporate issuer's legal obligations or credit standing. It creates a separate hedge position.",
            "Matching duration does not make coupon and redemption schedules identical. Residual tenor and curve-shape exposures can remain.",
            "A yield-only model still discounts promised cash flows without modelling recovery. Adding a hedge does not supply a missing credit-event model.",
        ),
    ),
    "vol_smile": (
        (
            "Low vega is weak price sensitivity to volatility; it does not uniquely determine intrinsic value. Deep-in-the-money or near-expiry contracts can both be ill-conditioned.",
            "Newton divides by vega. A near-zero denominator amplifies a premium residual into an unstable volatility step rather than improving convergence.",
            "Implied volatility is conditional on a model and current premium. Poor conditioning does not convert it into a guaranteed future realised volatility.",
            "Inversion can amplify premium bid-offer uncertainty when vega is small. Reporting only a midpoint volatility hides, rather than removes, that range.",
        ),
        (
            "Silent clamping replaces the observed target with another premium. Preserve and reject the inconsistent observation instead of reporting a fabricated valid root.",
            "The European-call upper bound applies even as volatility grows. An arbitrarily large volatility cannot reproduce a premium beyond that bound.",
            "Changing strike changes the contractual claim. A successful solve for that other claim does not validate the original quote.",
            "An iteration may stop because of stagnation or a limit. Success requires admissible inputs and a sufficiently small repricing residual.",
        ),
        (
            "A genuinely smooth fit does provide a continuous volatility display. The missing guarantee is price convexity, not visual continuity itself.",
            "A smooth fitted curve has some representation or interpolation rule. Naming that rule still does not establish no-arbitrage conditions.",
            "A supported volatility input can be converted to a model premium. The ability to compute it does not prove cross-strike convexity.",
            "A fitted parameterisation represents the slice by construction. Representation and small fit error are different from a no-arbitrage certificate.",
        ),
        (
            "The same contractual strike and today's premium can be used in both conventions. The difference concerns the surface response to a later spot move.",
            "Sticky rules are modelling choices for dynamics, not universal physical laws. Their suitability needs evidence and scenario testing.",
            "Fitting today's surface does not neutralise a portfolio's skew exposure. Risk depends on positions, hedge instruments and the assumed subsequent dynamics.",
            "Equal current values do not force equal derivatives under different movement rules. The implied-volatility response contributes through vega to effective delta.",
        ),
        (
            "The root reproduces a current premium under a quoting model. It does not observe or guarantee the stock's future path variation.",
            "One root contains no constraints across other strikes and expiries. A surface needs additional data, calibration and static-arbitrage controls.",
            "A physical probability of profit depends on a return distribution and the premium paid. It is not the volatility parameter returned by this inversion.",
            "A clean model inversion omits executable bid-offer, funding and other commercial terms. Matching a midpoint is not a dealer commitment.",
        ),
    ),
    "monte_carlo": (
        (
            "The buyer's historical return forecast belongs to a physical-measure view. It does not replace no-arbitrage carry in this pricing benchmark.",
            "Selecting drift to maximise a premium changes the valuation question and breaks the specified risk-neutral model. Inputs cannot be chosen to achieve a preferred output.",
            "Yesterday's sample return is a historical observation. Using it regardless of purpose mixes a physical estimate with the pricing measure.",
            "Generating random paths does not set a measure. Drift, carry, numeraire and discounting must be specified explicitly; zero drift is not universal.",
        ),
        (
            "Antithetic paths within each pair are deliberately dependent. Treating both as independent gives the wrong variance accounting and sample count.",
            "A seed identifies a reproducible random sequence; it is not a measured payoff variance. Estimate variance across the independent estimator observations.",
            "The largest payoff is an extreme observation, not a variance estimate of the sample mean. It discards the estimator's observation structure.",
            "Duplicating the analytic constant creates no simulated uncertainty evidence. The standard error must come from the actual random estimator observations.",
        ),
        (
            "Path count addresses sampling variance conditional on a model. It does not correct inappropriate dynamics, a wrong payoff or missing contractual events.",
            "The standard error scales approximately as one over square root of independent sample count. Quadrupling count therefore halves, rather than quarters, it.",
            "A nominal 95% confidence procedure can miss in individual runs. Additional paths narrow the interval without making its coverage a certainty.",
            "A wrong monitoring schedule defines a different simulated payoff. More samples estimate that wrong specification more precisely rather than repairing it.",
        ),
        (
            "A single missed interval is possible under a valid 95% procedure. Repeated coverage and convention checks are needed before attributing systematic bias.",
            "A fixed seed is a reproducibility control. Bias concerns the model or estimator expectation, not whether one realised sequence misses a benchmark.",
            "The interval is explicitly nominal 95%, not 100%. Expected coverage and certainty are different statements.",
            "The analytic value remains the benchmark for the matching contract. Replacing it by the sampled midpoint would erase the independent control.",
        ),
        (
            "Repeatability does not create bias. The relevant error is that coarse endpoint monitoring can implement a different barrier contract.",
            "A barrier depends on whether a crossing occurred at the specified observations. The final level alone cannot reconstruct continuous path survival.",
            "A large path count demonstrates sampling effort, not correct payoff or event handling. Contract validation must precede precision claims.",
            "The reported interval concerns sampling error under the implemented scheme. It does not automatically cover discretisation, input or economic model error.",
        ),
    ),
    "stochastic": (
        (
            "Brownian increments have zero mean. The correction comes from their squared increments accumulating nonzero quadratic variation, not from a drift in their mean.",
            "Ordinary dt-squared terms vanish at the relevant order. Squared diffusion increments survive because dW is of square-root-dt scale.",
            "Smoothness conditions matter for applying Itô, but the correction is not created by assuming away a payoff kink. Its source is quadratic variation.",
            "Itô's lemma is a transformation rule for a stochastic process. It does not depend on investor risk preferences or a change in their attitudes.",
        ),
        (
            "Unrecorded external cash breaks self-financing. Rebalancing must be funded consistently through the portfolio's stock and cash gains process.",
            "The ideal diffusion argument assumes continuous frictionless trading. It does not guarantee practical discrete-hedge results when costs and jumps matter.",
            "The terminal payoff identifies the derivative being replicated. Without it, the PDE and hedge argument do not determine a unique contract value.",
            "Today's hedge must be adapted to currently available information. Using future observations creates a hindsight strategy outside the replication assumptions.",
        ),
        (
            "Physical risk preferences need not vanish. Drift cancellation follows from the ideal self-financing replication, not universal indifference to risk.",
            "Historical returns can be nonzero. Their physical drift cancels algebraically in the replicating argument rather than being assumed zero in the data.",
            "A stock-dependent option is exactly why delta hedging is needed. Removing local diffusion exposure does not make its payoff independent of stock.",
            "Funding and dividend gains remain in the pricing PDE through carry and discounting. They are essential even though physical drift cancels.",
        ),
        (
            "Two representations of one model cannot certify mechanisms the model excludes, such as jumps, frictions or untradeable risks.",
            "A control comparing different payoffs is not an equality test of one price. Terminal and boundary conditions must encode the same contract.",
            "PDE discretisation and Monte Carlo sampling/time schemes have separate numerical errors. The theoretical representation does not remove those errors.",
            "Discounting and numeraire choice are part of the PDE/expectation link. Omitting them changes the valuation relationship.",
        ),
        (
            "Local Brownian cancellation is the ideal model result itself. The limitation in practice concerns mechanisms outside its continuous frictionless assumptions.",
            "The hedge still has a signed position fixed by the derivative exposure. Practical limitations do not remove the need to identify that sign.",
            "Under the stated smoothness assumptions a price derivative can exist. That mathematical property is not the practical zero-loss guarantee being questioned.",
            "The vanilla model can have a valid conditional pricing representation. Its existence does not certify actual trading execution or eliminate external model risks.",
        ),
    ),
    "barrier": (
        (
            "Equal final spot and strike give equal vanilla intrinsic values. The barrier difference comes from path survival, not a changed terminal vanilla payoff.",
            "A knock-out event changes the contract's live state, not its original strike. Rewriting the strike would define a different payoff.",
            "Under the stated knock-out rule, a later rally does not restore the terminated claim. Any rebate follows its own contractual terms.",
            "Monitoring history defines whether the barrier event occurred. Ignoring it replaces a path-dependent claim with a different terminal-only contract.",
        ),
        (
            "The two terminal states do not integrate across paths or discount cash flows to today. A current premium requires a supported valuation model.",
            "No physical path probabilities were supplied. A conditional cash amount does not identify the chance of profit after premium and costs.",
            "Unwind loss requires the actual signed pre-event hedge and feasible execution prices. The payoff table contains neither of those assumptions.",
            "A single FX path-payoff example contains no basket or joint-dynamics implementation. It cannot establish a general multi-asset capability.",
        ),
        (
            "Sharing a barrier label does not align strike, monitoring, expiry, rebate or settlement. The pathwise partition requires matching contractual terms.",
            "A rebate or changed expiry alters cash flows. Ignoring those changes breaks the matching payoff identity used to derive parity.",
            "The identity partitions all relevant paths, not only those ending at the starting level. That final-spot restriction is unnecessary and incorrect.",
            "Vanilla equals the sum of matching in and out values, which is one relation for two components. It does not determine each component separately.",
        ),
        (
            "A fixed seed makes an experiment reproducible. The monitoring error arises from missed crossings, not from the existence of a fixed seed.",
            "A continuous rule observes intervening crossings that a monthly rule may miss. They define different payoff events and generally different prices.",
            "Barrier survival depends on the path and monitoring definition. Volatility is a model input, not a sign that by itself determines an event.",
            "A sampling interval is conditional on the implemented monitoring scheme. It does not certify that discretisation or economic assumptions match the intended contract.",
        ),
        (
            "Execution exactly at the barrier is an idealisation, not a contractual market-liquidity guarantee. A gap can force a different exit price.",
            "The option's termination does not cancel losses on a separate hedge position. Those trades and their cash P&L must be reconciled.",
            "A premium is the initial option cash exchange. Realised profit also depends on payoff, hedging, costs and position direction.",
            "Delta hedging cancels local diffusion exposure under assumptions. A discontinuous gap cannot be neutralised by asserting continuous rebalancing.",
        ),
    ),
    "cds": (
        (
            "Under this buyer sign, spread widening creates a local gain in protection value. Total net economics can differ, but a universal buyer-loss rule is false.",
            "The existing coupon is contractual. Widening changes market value or quoted upfront, not the running coupon unless the contract explicitly resets it.",
            "A spread shock is not a qualifying default event. Protection settlement additionally depends on default, recovery and the actual settlement terms.",
            "Fixed contractual payments can gain or lose market value when current fair protection prices change. Fixed coupon does not imply fixed PV.",
        ),
        (
            "A positive premium rate and positive survival-discount annuity generally produce a nonzero premium-leg PV. Multiplication by zero has no basis here.",
            "Annual premium is one year's cash-flow scale. Future survival and payment timing enter the annuity used for the full premium-leg PV.",
            "Risky annuity is a survival-discounted accrual weight. Notional is the principal scale; the two have different units and roles.",
            "The difference is economic and temporal: cash per year versus discounted value of contingent payments. A display colour cannot define it.",
        ),
        (
            "Running premium is spread or contractual coupon times notional per year. Loss given default instead scales a protection payment after a credit event.",
            "Notional times loss given default is a currency amount. A probability is dimensionless and needs a distribution and horizon.",
            "Upfront and accrued premium are separate contractual cash flows. Computing gross default settlement does not make them zero.",
            "Actual credit-event settlement depends on documentation and conventions. The simplified gross LGD amount is not every production settlement calculation.",
        ),
        (
            "A fair market spread is not an automatic coupon-reset instruction. The old coupon remains fixed and the value difference appears in market value/upfront.",
            "The running coupon is a premium payment rate; recovery is a fraction of claim value in a credit-event assumption. Widening does not equate them.",
            "Past premiums are realised cash flows. A new fair spread does not retroactively cancel payments already made under the contract.",
            "A protection buyer pays running premium under this convention. Market widening can create a gain in value without turning that payment into guaranteed income.",
        ),
        (
            "The matched local parallel-spread number is precisely what a compatible CS01 hedge targets. The question asks for risks left after that cancellation.",
            "A local sensitivity offset is not a complete payoff replication. Default, recovery, liquidity and single-name/index differences can still generate losses.",
            "Buyer/seller sign is required to size the offset correctly. Matching a magnitude does not remove the need to identify signed exposure.",
            "A hedge does not alter the target contract's premium-payment definition. Running premium remains a cash flow regardless of whether one risk is offset.",
        ),
    ),
    "autocall": (
        (
            "Early redemption terminates the note's future schedule under these terms. Paying every later coupon would double count exposure that no longer exists.",
            "An autocall repays the current contract; it does not grant a free replacement note. Any reinvestment is a new decision on available market terms.",
            "A note already redeemed cannot re-enter its old final capital state. Applying maturity redemption again would repay the same principal twice.",
            "Redeemed principal returns the investor's capital. It is not all profit; coupons, initial investment, timing and costs determine net economics.",
        ),
        (
            "Memory stores specified missed entitlements but release remains conditional on the term sheet. It is not an unconditional promise that all coupons will pay.",
            "The example accumulates coupon amounts, not a stock-return-compounded balance. Compounding would require a separate contractual provision.",
            "An observation coupon and an annualised return have different time meanings. Memory does not remove observation timing, early redemption or payoff conditions.",
            "Coupon memory does not alter issuer default risk or the final principal-loss condition. Those are separate promises and event mechanisms.",
        ),
        (
            "Receipts contain repayment of invested principal. Net profit subtracts the initial outlay and relevant costs instead of counting all returned capital as income.",
            "One specified path supplies no distributional probabilities. It therefore cannot establish an expected return across possible outcomes.",
            "Annualisation needs actual cash-flow dates and an explicit return convention. A total receipt amount alone contains no unique annual rate.",
            "Fair value requires discounting and a model over possible future states. A realised or conditional cash-flow path is not that expectation.",
        ),
        (
            "The market condition does specify a promised principal payment under the contract. The missing guarantee concerns whether the issuer can honour that promise.",
            "The final observation rule is still needed to determine which promised capital state applies. A statement about issuer risk cannot replace that rule.",
            "The coupon threshold remains a defined contract input. Capital protection and issuer ability to pay are distinct from the existence of that threshold.",
            "The note continues to have a legal issuer with a credit exposure. A satisfied market-linked condition does not erase that counterparty.",
        ),
        (
            "Changing a title does not add a basket, worst-of event rule or joint-path implementation. The contract and model must actually be extended.",
            "A chart without quantified dependence assumptions cannot generate joint event probabilities. Valuation needs a specified, validated joint model.",
            "Worst-of coupons and calls depend on simultaneous basket states. Adding standalone prices does not apply that event logic or model dependence.",
            "Assuming all coupons pay removes the very contingent states being valued. Implement the term-sheet conditions on paths before averaging cash flows.",
        ),
    ),
    "var": (
        (
            "A quantile leaves a tail beyond its threshold. VaR does not cap the size of losses in that tail.",
            "The confidence statement concerns losses below a threshold, not positive profit. Losses smaller than VaR can still occur within that confidence region.",
            "A quantile is not an unconditional mean. Expected loss, VaR and tail expected shortfall summarise different features of a distribution.",
            "A calculated statistic does not create a governance threshold. Limit approval and its comparable metric/horizon must be supplied separately.",
        ),
        (
            "ES is a mathematical tail-loss summary. A coloured indicator is a presentation of a separate limit comparison and adds no tail definition.",
            "A tail average does not identify a future realised worst loss with certainty. The actual outcome can be larger or smaller.",
            "Coherence describes properties of a risk functional under conditions. It does not eliminate parameter, distribution or finite-tail-sample estimation error.",
            "A chosen stress is a conditional scenario. It does not acquire a calibrated physical probability from the existence of an ES calculation.",
        ),
        (
            "Nonlinear payoffs, changing sensitivities, jumps and dependence can break the assumed aggregation law. The square-root rule is not universal across regimes.",
            "Time scaling uses assumptions about return aggregation and exposure stability. It is more than changing a label from days to years.",
            "A smooth historical plot does not establish independent increments, stable variance or linear exposure. Those assumptions require explicit assessment.",
            "Changing the portfolio to fit a desired answer changes the question. Scaling must apply to the actual defined positions and horizon.",
        ),
        (
            "The number of scenario rows does not supply empirical frequencies. Probabilities need a separately justified distribution or calibration.",
            "A conditional stress and a Gaussian quantile answer different questions. Forcing agreement would hide the model limitation the stress may reveal.",
            "Removing adverse scenarios to preserve a limit destroys the risk assessment. Retain the scenario, investigate the loss and follow the appropriate escalation.",
            "Crisis dependence can differ from an estimated historical regime. Declare and test correlation assumptions instead of treating them as a guarantee.",
        ),
        (
            "A number returned by a calculator is not an approval. Without an actual comparable limit, the status must remain unassessed.",
            "Choosing a threshold after observing the result does not represent an approved limit. It fabricates a pass rather than applying risk governance.",
            "Positive notional gives scale, not an acceptable risk level. Limits also require a metric, horizon, confidence and authorised threshold.",
            "A within-VaR-limit observation would still leave tail and stress exposures. They should inform the decision rather than be omitted from it.",
        ),
    ),
}
