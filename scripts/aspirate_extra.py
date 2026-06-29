"""Extended universe — even more FX (full cross matrix + EM), more world/sector
indices, and international blue chips (Paris/Frankfurt/London/Tokyo/HK/Zurich/
Amsterdam) via exchange-suffixed tickers. Daily since inception, batched.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_spec = importlib.util.spec_from_file_location(
    "ae", os.path.join(os.path.dirname(os.path.abspath(__file__)), "aspirate_everything.py"))
ae = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ae)

FX_EXTRA = ("EURNOK=X EURSEK=X EURPLN=X EURHUF=X EURTRY=X EURZAR=X EURCZK=X EURDKK=X "
            "GBPCHF=X GBPCAD=X GBPAUD=X GBPNZD=X GBPSGD=X CHFJPY=X CADJPY=X NZDJPY=X "
            "AUDNZD=X AUDCAD=X AUDCHF=X EURCAD=X EURAUD=X EURNZD=X "
            "USDBRL=X USDINR=X USDKRW=X USDTHB=X USDPLN=X USDHUF=X USDCZK=X USDILS=X "
            "USDPHP=X USDMYR=X USDTWD=X USDCLP=X USDCOP=X USDIDR=X USDDKK=X USDHKD=X").split()

INDICES_EXTRA = ("^STOXX ^N100 ^SSMI ^AEX ^IBEX ^OMX ^OMXC25 ^OSEAX ^ATX ^SSEC ^STI "
                 "^JKSE ^NSEI ^KLSE ^NZ50 ^DJT ^DJU ^SOX ^XAU ^HUI ^RUI ^RUA ^XAX ^N300").split()

INTL = (
    # Paris (.PA)
    "MC.PA OR.PA AIR.PA SAN.PA BNP.PA TTE.PA SU.PA AI.PA EL.PA CS.PA DG.PA RMS.PA KER.PA "
    # Frankfurt (.DE)
    "SAP.DE SIE.DE ALV.DE DTE.DE BAS.DE BMW.DE MBG.DE BAYN.DE DB1.DE IFX.DE ADS.DE VOW3.DE "
    # London (.L)
    "HSBA.L AZN.L SHEL.L ULVR.L BP.L GSK.L RIO.L BATS.L DGE.L VOD.L BARC.L LLOY.L "
    # Tokyo (.T)
    "7203.T 6758.T 9984.T 6861.T 8306.T 9432.T 6098.T 7974.T 8035.T 4063.T "
    # Hong Kong (.HK)
    "0700.HK 9988.HK 0941.HK 1299.HK 0005.HK 3690.HK 1810.HK 0388.HK "
    # Zurich (.SW)
    "NESN.SW ROG.SW NOVN.SW UBSG.SW ZURN.SW ABBN.SW "
    # Amsterdam (.AS)
    "ASML.AS PRX.AS INGA.AS ADYEN.AS HEIA.AS "
    # Toronto (.TO) / Australia (.AX)
    "RY.TO TD.TO ENB.TO SHOP.TO BHP.AX CBA.AX CSL.AX"
).split()


def main():
    report = {}
    ae.batch_daily(FX_EXTRA, "fx_extra", report)
    ae.batch_daily(INDICES_EXTRA, "indices_extra", report)
    ae.batch_daily(INTL, "international_stocks", report)
    inv = ae.md.cache.inventory()
    report["cache_total_files"] = len(inv)
    report["cache_total_rows"] = sum(i["rows"] for i in inv)
    print("\n=== EXTRA UNIVERSE DONE ===")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
