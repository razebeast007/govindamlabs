import { useState } from "react";
import Eye from "./components/Eye";
import Card from "./components/Card";
import Navbar from "./components/Navbar";
import FlipkartTool from "./pages/Flipkart";
import AmazonTool from "./pages/Amazon";
import ReviewTool from "./pages/ReviewTool";

export default function App() {
  const [page, setPage] = useState("home");

  if (page === "flipkart") {
  return <FlipkartTool goBack={() => setPage("home")} />;
}

  if (page === "amazon") {
  return <AmazonTool goBack={() => setPage("home")} />;
}

  if (page === "review") {
  return <ReviewTool goBack={() => setPage("home")} />;
}
  return (
    <div className="
      min-h-screen 
      bg-gradient-to-br from-[#020617] to-[#0f172a]
      text-white
    ">
      <div className="absolute inset-0 pointer-events-none">
  <div className="absolute w-[400px] h-[400px] bg-purple-500/20 blur-[120px] top-[-100px] left-[-100px]" />
  <div className="absolute w-[400px] h-[400px] bg-blue-500/20 blur-[120px] bottom-[-100px] right-[-100px]" />
</div>
      <Navbar />
      <Eye />

      <div className="text-center mt-24">
        <h1 className="text-5xl font-bold">Product Data Lab</h1>
      </div>

      <div className="max-w-6xl mx-auto mt-16 grid md:grid-cols-3 gap-8 px-6">

        <Card
  title="Flipkart Image Extractor"
  desc="Extract images from Flipkart listings"
  open={() => setPage("flipkart")}
/>

<Card
  title="Amazon Image Extractor"
  desc="Extract images from Amazon listings"
  open={() => setPage("amazon")}
/>

<Card
  title="Review Finder"
  desc="Find product reviews instantly"
  open={() => setPage("review")}
/>

      </div>
    </div>
  );
}