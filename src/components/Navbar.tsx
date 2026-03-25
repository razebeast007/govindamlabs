export default function Navbar() {
  return (
    <div className="flex justify-center mt-6 px-4">
      <div className="
        flex justify-between items-center
        w-full max-w-6xl px-6 py-3
        bg-white/5 backdrop-blur-md
        border border-white/10 rounded-xl
      ">
        <h1 className="font-semibold text-white">
          Product Lab
        </h1>

        <div className="space-x-6 text-gray-400 text-sm">
          <a className="hover:text-white transition">Tools</a>
          <a className="hover:text-white transition">Docs</a>
          <a className="hover:text-white transition">Github</a>
        </div>
      </div>
    </div>
  );
}