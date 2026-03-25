import { useEffect, useRef, useState } from "react";
import "./eye.css";

export default function Eye() {
  const containerRef = useRef<HTMLDivElement>(null);
  const eyeRef = useRef<HTMLDivElement>(null);
  const pupilRef = useRef<HTMLDivElement>(null);

  const [text, setText] = useState("try catching me 😈");
  const [canCatch, setCanCatch] = useState(false);
  const [, setAttempts] = useState(0);

  // 🔥 FULL TROLL LINES (UNCHANGED)
  const trollLines = [
    "pakad ke dikha 😂","itna slow kyu hai?","bhai tu rehne de","try harder 😏",
    "nahi pakad payega tu","almost... but not really 😈","lagta hai practice chahiye",
    "haha miss ho gaya","tu thak jayega pehle 😂","skill issue detected ⚠️",
    "main fast hoon bhai","aur tez aa","itna easy nahi hoon main",
    "ye game tere bas ka nahi","😂 nice try","ab kya karega?",
    "bhai tu serious hai?","control kar mouse ko","lag raha hai panic ho gaya",
    "tu pakadne aya tha ya dance kar raha hai","😂 ye kya tha",
    "reflex kaha hai tere","slow motion me chal raha hai kya",
    "ye speed leke ayega tu?","bhai please improve","ye embarrassing ho raha hai",
    "aur koshish kar","fail ho gaya firse","main jeet gaya 😏",
    "tu haar gaya officially","bas bas rehne de","ye try count ho gaya",
    "😂😂 kya hi bolu","bhai tu legend hai apne level ka",
    "ye sab dekh ke maza aa raha hai","aur try kar entertainment mil raha hai",
    "tu pakad lega? dream on 😈","almost tha… almost 😂",
    "bhai tu cute try kar raha hai","ye kya strategy hai",
    "ab serious ho ja","lag raha hai give up karega",
    "ab to sympathy aa rahi hai","😂😂😂"
  ];

  const blastLines = [
    "ye acha nahi kiya tumne 😡","ab maza aaya?","khush ho gaya? 😂",
    "finally pakad liya?","bhai tu dangerous hai 😒","revenge mode on 😈",
    "game khatam nahi hua","tu obsessed ho gaya 😂","ye victory fake hai",
    "tu dangerous nahi... desperate lag raha hai","ye luck tha skill nahi 😏",
    "itna aggression kyu 😡","main wapas aaunga stronger 😈",
    "ab game interesting ho gaya","tu phas gaya bhai 😈",
    "ab maza aayega asli","game ab start hua hai"
  ];

  const random = (arr: string[]) =>
    arr[Math.floor(Math.random() * arr.length)];

  // 🏃 RUN AWAY
  const runAway = () => {
    const c = containerRef.current;
    if (!c) return;

    c.style.transition = "all 0.2s ease";
    c.style.left = Math.random() * (window.innerWidth - 120) + "px";
    c.style.top = Math.random() * (window.innerHeight - 120) + "px";
  };

  // 👁️ FOLLOW
  const moveEye = (e: MouseEvent) => {
    if (!eyeRef.current || !pupilRef.current) return;

    const rect = eyeRef.current.getBoundingClientRect();
    const dx = e.clientX - (rect.left + rect.width / 2);
    const dy = e.clientY - (rect.top + rect.height / 2);

    const angle = Math.atan2(dy, dx);

    pupilRef.current.style.transform =
      `translate(${Math.cos(angle) * 12}px, ${Math.sin(angle) * 12}px)`;
  };

  // 🎯 CHASE LOGIC
  const handleMove = (e: MouseEvent) => {
    const c = containerRef.current;
    if (!c) return;

    const rect = c.getBoundingClientRect();
    const dx = e.clientX - rect.left;
    const dy = e.clientY - rect.top;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < 140 && !canCatch) {
      setAttempts(prev => {
        const n = prev + 1;

        setText(random(trollLines));
        runAway();

        if (n > 150) {
          setCanCatch(true);
          setText("😏 chal ab pakad le laadle...");
        }

        return n;
      });
    }

    moveEye(e);
  };

  // 💥 PARTICLE BLAST
  const createEyeBlast = () => {
    const rect = eyeRef.current?.getBoundingClientRect();
    if (!rect) return;

    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;

    for (let i = 0; i < 120; i++) {
      const p = document.createElement("div");
      p.className = "eye-particle";

      const angle = Math.random() * Math.PI * 2;
      const distance = Math.random() * 600;

      const x = Math.cos(angle) * distance;
      const y = Math.sin(angle) * distance;

      p.style.left = cx + "px";
      p.style.top = cy + "px";
      p.style.setProperty("--x", `${x}px`);
      p.style.setProperty("--y", `${y}px`);

      document.body.appendChild(p);
      setTimeout(() => p.remove(), 2000);
    }
  };

  // 💀 CLICK
  const handleClick = () => {
    if (!canCatch) {
      setText("😂 abhi nahi pakad payega");
      runAway();
      return;
    }

    const eye = eyeRef.current;
    const c = containerRef.current;
    if (!eye || !c) return;

    setText(random(blastLines));

    // 🔴 flash
    const flash = document.createElement("div");
    flash.style.position = "fixed";
    flash.style.top = "0";
    flash.style.left = "0";
    flash.style.width = "100%";
    flash.style.height = "100%";
    flash.style.background = "rgba(255,0,0,0.3)";
    flash.style.zIndex = "9998";
    document.body.appendChild(flash);
    setTimeout(() => flash.remove(), 200);

    // 💥 shake
    document.body.classList.add("shake-screen");
    setTimeout(() => {
      document.body.classList.remove("shake-screen");
    }, 400);

    // 🔴 glow
    eye.style.boxShadow = "0 0 80px red, 0 0 160px red";

    // 💥 particles
    createEyeBlast();

    // 🌫️ smoke overlay
    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.background =
      "radial-gradient(circle, rgba(255,0,0,0.4), transparent)";
    overlay.style.zIndex = "9997";
    overlay.style.animation = "fadeSmoke 2s ease-out forwards";
    document.body.appendChild(overlay);
    setTimeout(() => overlay.remove(), 2000);

    // 👻 disappear
    setTimeout(() => {
      c.classList.add("fade-out");
    }, 200);

    // ✨ reappear + RESET
    setTimeout(() => {
      c.classList.remove("fade-out");

      c.style.left = Math.random() * (window.innerWidth - 120) + "px";
      c.style.top = Math.random() * (window.innerHeight - 120) + "px";

      c.classList.add("fade-in");
      setTimeout(() => c.classList.remove("fade-in"), 500);

      eye.style.boxShadow = "";

      setText("😂 wapas aa gaya...");
      setAttempts(0);      // 🔥 RESET COUNT
      setCanCatch(false);  // restart game
    }, 2000);
  };

  // 🎮 EVENT
  useEffect(() => {
    window.addEventListener("mousemove", handleMove);
    return () => window.removeEventListener("mousemove", handleMove);
  }, [canCatch]);

  useEffect(() => {
  const handler = (e: any) => {
    setText(e.detail);
  };

  window.addEventListener("eyeText", handler);

  return () => {
    window.removeEventListener("eyeText", handler);
  };
}, []);

  return (
    <div
      ref={containerRef}
      style={{
        position: "fixed",
        bottom: "30px",
        left: "30px",
        zIndex: 9999
      }}
    >
      <div className="thought">{text}</div>

      <div ref={eyeRef} className="eye" onClick={handleClick}>
        <div ref={pupilRef} className="pupil"></div>
      </div>
    </div>
  );
}