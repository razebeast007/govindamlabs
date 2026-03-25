import { useState } from "react";

export default function ReviewTool({ goBack }: any) {

  const [link, setLink] = useState("");
  const [fixedLink, setFixedLink] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [reviewUrl, setReviewUrl] = useState<string | null>(null);
  const [finding, setFinding] = useState(false);

  // 🔥 GET REVIEWS
  const getReviews = async () => {
    if (!fixedLink || finding) return;

    setFinding(true);
    setReviewUrl(null);

    try {
      const res = await fetch("https://govindamlabs.onrender.com/find-review-page", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ links: [fixedLink] })
      });

      const data = await res.json();

      if (data.found) {
        setReviewUrl(data.url);
      }
 
      else {
        alert("❌ No review found");
      }

    } catch {
      alert("Error 💀");
    }

    setFinding(false);
  };

  // 🔥 FIX LINK
  const fixLink = async () => {
    if (!link || loading) {
      alert("Link daal pehle 😒");
      return;
    }

    setLoading(true);
    setFixedLink(null);
    setReviewUrl(null); // 🔥 important reset

    try {
      const res = await fetch("https://govindamlabs.onrender.com/fix-flipkart-link", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ links: [link] })
      });

      const data = await res.json();
      setFixedLink(data.fixed[0]);

    } catch {
      alert("Error hua 💀");
    }

    setLoading(false);
  };

  const scrollTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const scrollBottom = () => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  };

  const reset = () => {
    setLink("");
    setFixedLink(null);
    setReviewUrl(null); // 🔥 FIX
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#020617] to-[#0f172a] text-white relative">

      {/* 🔝 TOP BAR */}
      <div className="flex justify-between items-center px-6 py-4">
        <button
          onClick={goBack}
          className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition"
        >
          ← Back
        </button>
      </div>

      {/* 🧊 MAIN CARD */}
      <div className="max-w-3xl mx-auto mt-20 px-6">
        <div className="p-8 rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10 shadow-[0_0_60px_rgba(0,0,0,0.5)]">

          <h1 className="text-4xl font-bold text-center mb-8 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Flipkart Review Extractor
          </h1>

          {/* INPUT */}
          <textarea
            value={link}
            onChange={(e) => setLink(e.target.value)}
            placeholder="Paste Flipkart product link here..."
            className="w-full h-32 p-4 rounded-xl bg-black/40 border border-white/10 focus:outline-none focus:border-purple-500 resize-none text-gray-200"
          />

          {/* BUTTONS */}
          <div className="flex gap-4 mt-6">

            <button
              onClick={fixLink}
              disabled={loading}
              className="flex-1 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 hover:scale-[1.02] transition-all duration-300 disabled:opacity-50"
            >
              {loading ? "Fixing..." : "Fix Link"}
            </button>

            <button
              onClick={reset}
              className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-red-500/20 hover:border-red-400/30 transition-all duration-300"
            >
              Reset
            </button>

          </div>

          {/* RESULT */}
          {fixedLink && (
            <div className="mt-6">

              <div className="p-4 rounded-xl bg-black/40 border border-white/10 break-all text-green-400">
                {fixedLink}
              </div>

              {reviewUrl && (
  <div className="mt-4 p-3 bg-black/40 border border-white/10 rounded text-green-400 break-all">
    {reviewUrl}
  </div>
)}

<button
  onClick={getReviews}
  disabled={finding}
  className="
    w-full mt-4 py-3 rounded-xl 
    bg-green-500 hover:bg-green-600 
    transition disabled:opacity-50
  "
>
  {finding ? "Searching..." : reviewUrl ? "Mil Gaya 😈" : "Get Reviews"}
</button>


            </div>
          )}

        </div>
      </div>

      {/* FLOATING */}
      <div className="fixed right-6 bottom-10 flex flex-col gap-3">

        <button
          onClick={scrollTop}
          className="w-10 h-10 rounded-full bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10 hover:text-white transition backdrop-blur-md"
        >
          ↑
        </button>

        <button
          onClick={scrollBottom}
          className="w-10 h-10 rounded-full bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10 hover:text-white transition backdrop-blur-md"
        >
          ↓
        </button>

      </div>

    </div>
  );
}