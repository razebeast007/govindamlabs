type Props = {
  title: string;
  desc: string;
  open: () => void;
};

export default function Card({ title, desc, open }: Props) {

  // 🔥 dynamic lines per card
  const cardLines: any = {

  "Flipkart Image Extractor": [
    "ye heavy tool hai 😈","samajh ke use kar","tu ready hai?",
    "ab maza aayega","dangerous lag raha hai 😂",

    "bhai tu overconfident lag raha hai",
    "ye tere level ka nahi hai",
    "ab tu fasa 😈",
    "ye galat haath me dangerous hai",
    "bhai soch le ek baar",
    "ye khel nahi hai",
    "tu ready nahi hai abhi",
    "confidence zyada hai tera 😂",
    "ab pachtaega",
    "ye game ulta pad sakta hai",
    "bhai tu serious ho gaya",
    "ab kuch bada hone wala hai",
    "tu sambhal paayega?",
    "ab control nahi rahega",
    "ye risky decision hai",
    "bhai tu khel raha hai aag se 🔥",
    "ab tu ruk nahi paayega",
    "ye addictive hai 😏",
    "ab tu fass gaya",
    "ye trap lag raha hai",
    "bhai tu galti kar raha hai",
    "ab regret karega",
    "ye safe nahi hai",
    "ab tu control me nahi hai",
    "tu khud ko overestimate kar raha hai",
    "ye advanced level hai",
    "bhai tu beginner hai abhi",
    "ab tu seekhega dard 😂",
    "ye dangerous territory hai",
    "ab game serious ho gaya",
    "bhai tu limit cross kar raha hai",
    "ye illegal vibes de raha hai 😈",
    "ab tu bhaag nahi paayega",
    "ye dark zone hai",
    "bhai tu kahan aa gaya",
    "ab tu fas gaya pakka",
    "ye tere control se bahar hai",
    "bhai tu risk le raha hai",
    "ab kuch bhi ho sakta hai",
    "ye unpredictable hai",
    "tu ready nahi hai mentally",
    "ab tu regret karega pakka",
    "ye galat jagah aa gaya tu",
    "bhai tu phas chuka hai",
    "ye last warning hai 😏",
    "ab tu bach nahi paayega",
    "bhai tu dangerous ban raha hai",
    "ye power handle nahi hogi tujhse",
    "ab tu khud ko nahi rok paayega"
  ],

  "Amazon Image Extractor": [
    "safe choice 😂","basic banda hai tu","easy mode select kiya",
    "kuch risky kar na","boring but safe 😏",

    "bhai tu safe player hai",
    "koi surprise nahi diya tune",
    "expected tha ye 😂",
    "tu kabhi risk lega?",
    "bhai tu predictable hai",
    "ye sab karte hai",
    "kuch naya try kar na",
    "tu comfort zone me hai",
    "bhai tu basic hai",
    "ye beginner level hai",
    "tu upgrade kab karega?",
    "bhai tu safe game khel raha hai",
    "ye sabko aata hai",
    "tu thoda daring ban",
    "bhai tu boring ho raha hai",
    "same old same old",
    "tu explore nahi karta",
    "bhai tu risk se darta hai",
    "ye easy choice hai",
    "kuch hatke kar",
    "tu adventurous nahi hai",
    "bhai tu low effort laga raha hai",
    "ye safe but useless hai",
    "tu kab grow karega?",
    "bhai tu basic hi rahega",
    "ye sab kar lete hai",
    "tu unique nahi hai 😂",
    "bhai tu safe zone ka king hai",
    "ye default option tha",
    "tu experiment nahi karta",
    "bhai tu slow grow karega",
    "ye normal banda ka choice hai",
    "tu alag nahi hai",
    "bhai tu copy paste hai",
    "ye sab same hai",
    "tu standout nahi karta",
    "bhai tu average hai",
    "ye sabko aata hai",
    "tu impress nahi kar raha",
    "bhai tu chill mode me hai",
    "ye safe hai but weak hai",
    "tu better kar sakta tha",
    "bhai tu lazy hai",
    "ye effort nahi laga",
    "tu try hi nahi kar raha",
    "bhai tu risk avoid kar raha",
    "ye comfort zone addiction hai",
    "tu safe khel khel ke haar jayega",
    "bhai tu predictable AI jaisa hai",
    "ye safe but boring combo hai"
  ],

  "Review Finder": [
    "judge karne aaya hai? 😂","analysis mode on 😏",
    "bhai doubt hi doubt","tu trust nahi karta kisi pe",
    "deep thinker ban gaya",

    "bhai tu overthink kar raha hai",
    "itna research kyu 😂",
    "tu confuse hi rahega",
    "bhai tu decision nahi lega",
    "analysis paralysis 😂",
    "tu bas scroll karega",
    "bhai tu doubt machine hai",
    "kuch kharidega bhi?",
    "tu trust issues wala hai",
    "bhai tu skeptic hai",
    "itna mat soch",
    "tu khud pe trust kar",
    "bhai tu overanalyze kar raha hai",
    "ye sab useless hai",
    "tu kab action lega?",
    "bhai tu stuck hai",
    "ye sab time waste hai",
    "tu conclusion nahi nikaalega",
    "bhai tu confused rahega",
    "itna deep kyu ja raha hai",
    "tu khud ko hi doubt karega",
    "bhai tu lost hai",
    "ye sab dekh ke kya karega",
    "tu overthinker hai",
    "bhai tu decision nahi le paayega",
    "ye sab noise hai",
    "tu clarity nahi laa raha",
    "bhai tu loop me hai",
    "tu bas compare karta rahega",
    "bhai tu stuck hai yahi",
    "ye endless cycle hai",
    "tu kab rukega?",
    "bhai tu obsessive hai 😂",
    "tu review addict hai",
    "bhai tu reality bhool gaya",
    "itna bhi serious mat ho",
    "tu khud ko confuse kar raha",
    "bhai tu trap me hai",
    "ye sab illusion hai",
    "tu clarity lose kar raha",
    "bhai tu overloading kar raha",
    "tu decision fatigue me hai",
    "bhai tu stuck mode me hai",
    "ye sab infinite loop hai",
    "tu kab break lega?",
    "bhai tu thinking machine ban gaya",
    "tu khud ko doubt karega",
    "bhai tu analysis me doob gaya",
    "ye sab unnecessary hai",
    "tu bas sochta hi rahega"
  ]
};

  const random = (arr: string[]) =>
    arr[Math.floor(Math.random() * arr.length)];

  // 😈 hover pe eye ko message
  const react = () => {
    const arr = cardLines[title] || ["😂 interesting choice"];
    const text = random(arr);

    window.dispatchEvent(new CustomEvent("eyeText", { detail: text }));
  };

  // 💥 click pe aggressive reaction
  const clickReact = () => {
    window.dispatchEvent(
      new CustomEvent("eyeText", { detail: "😈 tu andar ja raha hai..." })
    );

    open();
  };

  return (
    <div
      onMouseEnter={react}
      className="
        group
        p-6 rounded-2xl 
        bg-white/5 backdrop-blur-xl
        border border-white/10 
        transition-all duration-300 
        cursor-pointer

        hover:border-purple-400/40
        hover:bg-white/10
        hover:scale-[1.04]
        hover:shadow-[0_0_60px_rgba(168,85,247,0.4)]
      "
    >
      {/* 🔥 top glow line */}
      <div className="
        h-[2px] w-0 bg-gradient-to-r from-purple-500 to-blue-500
        transition-all duration-300
        group-hover:w-full mb-4
      " />

      <h2 className="mb-2 text-lg font-semibold">
        {title}
      </h2>

      <p className="text-gray-400 mb-6">
        {desc}
      </p>

      <button
        onClick={clickReact}
        className="
          w-full
          bg-gradient-to-r from-purple-500 to-blue-500 
          text-white px-4 py-2 rounded-lg
          transition-all duration-300

          hover:scale-105
          hover:shadow-[0_0_20px_rgba(168,85,247,0.6)]
        "
      >
        Open Tool
      </button>
    </div>
  );
}