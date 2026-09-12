"use client";

import { useState } from "react";
import { Navigation } from "@/components/landing/navigation";
import { FooterSection } from "@/components/landing/footer-section";
import { Plus, Minus, ChevronRight } from "lucide-react";

interface FAQItem {
  question: string;
  answer: React.ReactNode;
}

export default function FAQPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs: FAQItem[] = [
    {
      question: "What is IRIS X / Aditya-L1 Solar Flare Forecasting?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            IRIS X is an ensemble machine learning and sequence-modeling pipeline built to monitor, preprocess, and predict solar flare activity in real time. It processes soft and hard X-ray data gathered by payload instruments on India’s first solar observatory mission, Aditya-L1.
          </p>
          <p>
            The system provides researchers and space weather operators with continuous, explainable forecasting to warn against high-energy solar events that could impact satellite instrumentation or communications infrastructure.
          </p>
        </div>
      ),
    },
    {
      question: "Which instruments on Aditya-L1 does this pipeline ingest?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            We ingest live telemetry from two critical payloads:
          </p>
          <ul className="list-disc pl-5 space-y-2">
            <li>
              <strong>SoLEXS (Solar Low Energy X-ray Spectrometer):</strong> Providing continuous 1-minute cadence measurements in the 1–22 keV range, vital for identifying low-energy thermal pre-cursors.
            </li>
            <li>
              <strong>HEL1OS (High Energy L1 Orbiting X-ray Spectrometer):</strong> Monitoring hard X-ray bands in the 10–150 keV range, capturing solar flare impulsive phases and non-thermal emission spectra.
            </li>
          </ul>
        </div>
      ),
    },
    {
      question: "What kind of machine learning models power the pipeline?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            Our system uses a four-stage ensemble architecture:
          </p>
          <ul className="list-disc pl-5 space-y-2">
            <li>
              <strong>LSTM Forecasting:</strong> Processes historical 60-minute X-ray flux sequences to project solar flare probability horizons (15m, 30m, and 60m).
            </li>
            <li>
              <strong>LightGBM Stacking Meta-Learner:</strong> Aggregates primary sequence outputs, rolling derivatives, and statistical baseline indicators to optimize decision boundaries.
            </li>
            <li>
              <strong>Isolation Forest:</strong> Acts as a real-time anomaly filter, flagging data spikes and solar instrument telemetry glitches before triggers are sent.
            </li>
            <li>
              <strong>SHAP Explanation Engine:</strong> Calculates real-time Shapley attributions, detailing precisely which bands and features influenced the current flare risk projection.
            </li>
          </ul>
        </div>
      ),
    },
    {
      question: "What are the forecast cadences and lead times?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            Pre-processed telemetry from SoLEXS and HEL1OS is evaluated at a continuous 1-minute cadence. The pipeline outputs forecast horizons at 15-minute, 30-minute, and 60-minute lead times.
          </p>
        </div>
      ),
    },
    {
      question: "Can I use my own models with your data catalog?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            Yes. Our dataset collection is fully compatible with standard Python science libraries. We provide an API client library (<code>adityal1</code>) to easily import raw telemetry and pre-processed bands into PyTorch, TensorFlow, or Scikit-learn pipelines.
          </p>
        </div>
      ),
    },
    {
      question: "Is this pipeline affiliated with ISRO?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            This is an independent research pipeline developed to utilize open-access data from the Aditya-L1 science payloads available via ISRO's ISSDC and PRADAN portal.
          </p>
        </div>
      ),
    },
    {
      question: "How do I cite the IRIS X pipeline in publications?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            You can cite the IRIS X pipeline project using the following BibTeX entry:
          </p>
          <pre className="p-4 bg-muted font-mono text-xs rounded border overflow-x-auto leading-relaxed">
{`@article{irisx2026adityal1,
  title={IRIS X: Real-Time Solar Flare Forecasting and Explainable AI for Aditya-L1},
  author={Narayana, Aditya and Team},
  journal={Space Weather and Machine Learning Review},
  year={2026},
  url={https://github.com/Narayana1729/Aditya-L1-Solar-Flare-Forecasting}
}`}
          </pre>
        </div>
      ),
    },
    {
      question: "How can I get access to the dashboard?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            You can launch the dashboard by clicking "Launch Dashboard" in the navigation bar. The dashboard provides real-time visualization of telemetry inputs, active SHAP attributions, and predicted flare probabilities.
          </p>
        </div>
      ),
    },
    {
      question: "How can I get support or report pipeline anomalies?",
      answer: (
        <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
          <p>
            You can submit issue tickets or reach out via our GitHub repository. We also encourage researchers to participate in our open-source discussions.
          </p>
        </div>
      ),
    },
  ];

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Navigation />
      
      {/* Top spacing to account for fixed navigation */}
      <main className="flex-grow pt-32 pb-24 max-w-4xl mx-auto px-6 w-full">
        {/* Page Header */}
        <div 
          className="mb-12 border-b border-border pb-6"
          style={{ fontFamily: "'Google Sans', system-ui, -apple-system, sans-serif" }}
        >
          <h1 className="text-4xl font-normal tracking-tight mb-4">FAQ</h1>
          <p className="text-muted-foreground text-sm font-normal">
            Frequently asked questions about the IRIS X Solar Flare Forecasting pipeline, Aditya-L1 instruments, and machine learning architectures.
          </p>
        </div>

        {/* Collapsible Q&A list */}
        <div 
          className="space-y-4"
          style={{ fontFamily: "'Google Sans', system-ui, -apple-system, sans-serif" }}
        >
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div 
                key={index} 
                className="border-b border-border/60 pb-4 transition-all duration-300"
              >
                <button
                  onClick={() => toggleFAQ(index)}
                  className="w-full flex items-center justify-between text-left py-3 group cursor-pointer"
                >
                  <span className="font-semibold text-lg text-foreground group-hover:text-[#FF5C28] transition-colors flex items-center gap-3">
                    <ChevronRight className={`w-4 h-4 text-[#FF5C28] transition-transform duration-300 ${isOpen ? "rotate-90" : ""}`} />
                    {faq.question}
                  </span>
                  <span className="shrink-0 ml-4 text-muted-foreground/60 group-hover:text-foreground">
                    {isOpen ? (
                      <Minus className="w-4 h-4" />
                    ) : (
                      <Plus className="w-4 h-4" />
                    )}
                  </span>
                </button>
                <div 
                  className={`grid transition-all duration-300 overflow-hidden ${
                    isOpen ? "grid-rows-[1fr] opacity-100 mt-2 pl-7" : "grid-rows-[0fr] opacity-0 pl-7"
                  }`}
                >
                  <div className="overflow-hidden">
                    {faq.answer}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </main>

      <FooterSection />
    </div>
  );
}
