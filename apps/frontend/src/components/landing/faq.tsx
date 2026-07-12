import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Reveal } from "@/components/landing/reveal";

const faqs = [
  {
    question: "What kind of video do I need?",
    answer:
      "A single smartphone recording of the full match, filmed from one elevated angle covering as much of the pitch as possible. No special cameras or drones required.",
  },
  {
    question: "Who is Scout AI built for?",
    answer:
      "Schools, academies, township clubs, amateur teams, and women's teams, anyone who wants professional-grade analysis without a professional-grade budget.",
  },
  {
    question: "Does the AI make up statistics?",
    answer:
      "No. The AI report only explains numbers the computer-vision pipeline actually measured from your video: possession, distances, positions. It never invents figures.",
  },
  {
    question: "How long does analysis take?",
    answer:
      "Processing time depends on match length and current queue load. You'll see live status as your match moves through detection, tracking, and report generation.",
  },
  {
    question: "Is my match data private?",
    answer:
      "Your videos and reports are never used to train models or shared with other teams. This is an early build without user accounts yet, so treat uploads as accessible to anyone with the match link for now.",
  },
];

export function Faq() {
  return (
    <section id="faq" className="border-t border-border px-6 py-24">
      <div className="mx-auto max-w-2xl">
        <Reveal className="text-center">
          <h2 className="font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            Frequently Asked Questions
          </h2>
        </Reveal>

        <Reveal delay={0.1} className="mt-12">
          <Accordion>
            {faqs.map((faq) => (
              <AccordionItem key={faq.question} value={faq.question}>
                <AccordionTrigger className="text-left">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Reveal>
      </div>
    </section>
  );
}
