import { useRef, useState } from "react";

export default function AmazonTool({ goBack }: any) {

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  // 🔥 MAIN EXTRACT FUNCTION
  const extract = async () => {
    const raw = textareaRef.current?.value || "";
    const links = raw.split("\n").filter(l => l.trim());

    if (links.length === 0) {
      alert("Links daal pehle 😒");
      return;
    }

    setLogs([]);
    setLoading(true);
    setProgress(5);
    setDownloadUrl(null);

    try {
      const response = await fetch("http://178.104.72.19:8000/extract-amazon-live", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ links })
      });

      if (!response.body) throw new Error("No stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";
      let doneCount = 0;
      const total = links.length;
      let downloadTriggered = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (let part of parts) {
          if (part.startsWith("data: ")) {
            try {
              const data = JSON.parse(part.replace("data: ", ""));

              // 🧠 LOGS
              if (data.status) {
                setLogs(prev => [...prev, data.status]);

                // 🔥 PROGRESS
                if (data.status.includes("Processing")) {
                  doneCount++;
                  const percent = Math.min(95, Math.floor((doneCount / total) * 100));
                  setProgress(percent);
                }
              }

              // 📦 DONE
              if (data.done && !downloadTriggered) {
                downloadTriggered = true;

                setProgress(100);

                if (data.filename) {
                const zipUrl = `http://178.104.72.19:8000/download/${data.filename}`;
                setDownloadUrl(zipUrl);
                } else {
                  alert("No images found ❌");
                }
              }

            } catch (e) {
              console.warn("Parse error:", e);
            }
          }
        }
      }

    } catch (err) {
      console.error(err);
      alert("Error hua 💀");
    }

    setLoading(false);
  };

  // 🔝 scroll
  const scrollTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const scrollBottom = () => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  };

  // 🔄 reset
  const reset = () => {
    if (textareaRef.current) textareaRef.current.value = "";
    setDownloadUrl(null);
    setProgress(0);
    setLogs([]);
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
            Amazon Image Extractor
          </h1>

          {/* 📝 TEXTAREA */}
          <textarea
            ref={textareaRef}
            placeholder="Paste Amazon product links here..."
            className="w-full h-44 p-4 rounded-xl bg-black/40 border border-white/10 focus:outline-none focus:border-purple-500 resize-none text-gray-200"
          />

          {/* 🔥 BUTTONS */}
          <div className="flex gap-4 mt-6">

            <button
              onClick={extract}
              disabled={loading}
              className="flex-1 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 hover:scale-[1.02] transition-all duration-300 disabled:opacity-50"
            >
              {loading ? "Processing..." : "Extract Images"}
            </button>

            <button
              onClick={reset}
              className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-red-500/20 hover:border-red-400/30 transition-all duration-300"
            >
              Reset
            </button>

          </div>

          {/* 🔥 PROGRESS */}
          {loading && (
            <div className="mt-5">
              <div className="w-full bg-white/10 rounded-full h-2">
                <div
                  className="h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Processing... {progress}%
              </p>
            </div>
          )}

          {/* 📜 LOGS */}
          {logs.length > 0 && (
            <div className="mt-4 max-h-40 overflow-y-auto text-xs text-gray-400 bg-black/30 p-3 rounded">
              {logs.map((log, i) => (
                <div key={i}>{log}</div>
              ))}
            </div>
          )}

          {downloadUrl && (
  <button
    onClick={() => window.location.href = downloadUrl}
    className="mt-6 block text-center py-3 rounded-xl bg-green-500 hover:bg-green-600 transition"
  >
    Download ZIP 📦
  </button>
)}

        </div>
      </div>

      {/* ⚡ FLOATING */}
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