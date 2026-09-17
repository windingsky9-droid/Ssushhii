from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEMO_JS = r'''const $=id=>document.getElementById(id);
const peers=["SPY","QQQ","AAPL","MSFT","NVDA","AMZN","META","GOOGL"];
function hashScore(t,s,lo,hi){let h=2166136261;for(const c of `${t}:${s}`){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return lo+(Math.abs(h)%(hi-lo+1));}
function ticker(v){const t=(v||"").trim().toUpperCase();if(!/^[A-Z0-9][A-Z0-9.-]{0,9}$/.test(t))throw new Error("Enter a ticker using letters, numbers, dots, or hyphens.");return t;}
function snapshot(t){const c=hashScore(t,"composite",38,92),m=hashScore(t,"momentum",30,88),r=hashScore(t,"rsi",34,72),v=hashScore(t,"vol",14,48)/100,b=hashScore(t,"beta",55,155)/100,p=c>=70?"Constructive":c>=50?"Mixed":"Defensive";return{ticker:t,composite_score:c,posture:p,summary:`${t} shows a ${p.toLowerCase()} synthetic demo factor profile.`,as_of:"Synthetic public preview — not live market data",metrics:{momentum:m,rsi:r,realized_vol:v,beta:b},market:{regime:"Balanced demo regime",note:"Illustrative context for product evaluation only."},comparables:peers.filter(x=>x!==t).slice(0,4)};}
function render(d){const s=Math.max(0,Math.min(100,d.composite_score));$("result-title").textContent=`${d.ticker} / Research snapshot`;$("source-badge").textContent="DEMO DATA";$("composite-score").textContent=s;$("score-meter").style.width=`${s}%`;$("posture").textContent=d.posture;$("summary").textContent=d.summary;$("as-of").textContent=d.as_of;$("metric-momentum").textContent=d.metrics.momentum;$("metric-rsi").textContent=d.metrics.rsi;$("metric-vol").textContent=`${(d.metrics.realized_vol*100).toFixed(1)}%`;$("metric-beta").textContent=d.metrics.beta.toFixed(2);$("market-regime").textContent=d.market.regime;$("market-note").textContent=d.market.note;$("comparables").innerHTML="";d.comparables.forEach(p=>{const e=document.createElement("span");e.textContent=p;$("comparables").appendChild(e)});}
function run(v){const status=$("form-status"),err=$("research-error");err.hidden=true;try{render(snapshot(ticker(v)));status.className="form-status";status.textContent="Synthetic demo snapshot loaded — no live market data or payment connection.";}catch(e){status.className="form-status error";status.textContent=e.message;err.textContent=e.message;err.hidden=false;}}
document.getElementById("research-form").addEventListener("submit",e=>{e.preventDefault();run(document.getElementById("ticker-input").value)});
document.addEventListener("DOMContentLoaded",()=>run(document.getElementById("ticker-input").value));'''

def build_public_demo(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    html = html.replace("{{ url_for('static', filename='styles.css') }}", "styles.css")
    html = html.replace("{{ url_for('static', filename='app.js') }}", "app.js")
    html = html.replace(
        "Demo mode works instantly. Connect Factor Weave later for live provider data.",
        "Public synthetic demo — no live market data or payment connection.",
    )
    html = html.replace("Checkout activates only after payment links are configured.", "This preview does not take payments.")
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    (output_dir / "styles.css").write_text((ROOT / "static" / "styles.css").read_text(encoding="utf-8"), encoding="utf-8")
    (output_dir / "app.js").write_text(DEMO_JS, encoding="utf-8")


if __name__ == "__main__":
    build_public_demo(ROOT / "public-demo")
    print("Built public-demo/")
