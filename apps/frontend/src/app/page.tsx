import { SiteHeader } from "@/components/landing/site-header";
import { Hero } from "@/components/landing/hero";
import { Mission } from "@/components/landing/mission";
import { Features } from "@/components/landing/features";
import { HowItWorks } from "@/components/landing/how-it-works";
import { Vision } from "@/components/landing/vision";
import { Technology } from "@/components/landing/technology";
import { Faq } from "@/components/landing/faq";
import { SiteFooter } from "@/components/landing/site-footer";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col">
      <SiteHeader />
      <main className="flex-1">
        <Hero />
        <Mission />
        <Features />
        <HowItWorks />
        <Vision />
        <Technology />
        <Faq />
      </main>
      <SiteFooter />
    </div>
  );
}
