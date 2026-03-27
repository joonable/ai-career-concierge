import { Inter, Playfair_Display } from "next/font/google";

import { WovenLightHero } from "@/components/home/woven-light-hero";

const headlineFont = Playfair_Display({
  subsets: ["latin"],
  weight: "700",
});

const bodyFont = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export default function HomePage() {
  return (
    <main>
      <WovenLightHero
        headlineClassName={headlineFont.className}
        bodyClassName={bodyFont.className}
      />
    </main>
  );
}
