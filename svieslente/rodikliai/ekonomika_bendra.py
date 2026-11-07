"""Bendros ekonomikos rodiklių priemonės."""
import plotly.graph_objects as go

from .bendra import SERIJOS, linijos, stilius


def grafikas(serijos, pavadinimas, paantraste, saltinis, nuo="2010-01-01", vnt=" %", zenklas=False,
             nulio_linija=True, nuo_nulio=True, metiniai=False, dec=1):
    """Linijinis grafikas: serijos = [(pavadinimas, Series), ...] – spalvos pagal eilės tvarką."""
    f = go.Figure()
    linijos(f, [(v, s[s.index >= nuo], SERIJOS[i]) for i, (v, s) in enumerate(serijos)],
            vnt=vnt, zenklas=zenklas, dec=dec, zymekliai=metiniai, nuo_nulio=nuo_nulio)
    stilius(f, pavadinimas, paantraste, saltinis, vnt=vnt, nulio_linija=nulio_linija, metiniai=metiniai)
    if not metiniai:
        f.update_xaxes(tickformat="%Y")
        f.update_layout(xaxis_hoverformat="%Y-%m")
    if nuo_nulio:
        f.update_yaxes(rangemode="tozero")
    return f
