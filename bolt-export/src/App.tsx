import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Hero from './components/Hero';
import TrustStrip from './components/TrustStrip';
import IntroSection from './components/IntroSection';
import WorkSection from './components/WorkSection';
import MarqueeZone from './components/MarqueeZone';
import ServicesSection from './components/ServicesSection';
import AboutSection from './components/AboutSection';
import Calculator from './components/Calculator';
import StatementCTA from './components/StatementCTA';
import ContactSection from './components/ContactSection';
import Playground from './components/Playground';
import SiteFooter from './components/SiteFooter';
import WorkModal from './components/WorkModal';
import Wizard from './components/Wizard';
import KnowledgeCentre from './pages/KnowledgeCentre';
import KcComingSoon from './pages/KcComingSoon';
import { WizardProvider, useWizard } from './context/WizardContext';
import { ModalProvider } from './context/ModalContext';

/** The existing homepage, unchanged, just moved into its own component. */
function HomePage() {
  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            const d = +(en.target.getAttribute('data-rvd') || 0);
            if (d) {
              setTimeout(() => en.target.classList.add('in-view'), d);
            } else {
              en.target.classList.add('in-view');
            }
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.18 }
    );
    document.querySelectorAll('.rv').forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return (
    <>
      <Hero />
      <TrustStrip />
      <IntroSection />
      <WorkSection />
      <MarqueeZone />
      <ServicesSection />
      <AboutSection />
      <Calculator />
      <StatementCTA />
      <ContactSection />
      <Playground />
    </>
  );
}

function AppInner() {
  const { openWizard } = useWizard();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('wizard') === '1') openWizard();
  }, [openWizard]);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <Navigation />
      <main id="main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/resources" element={<KnowledgeCentre />} />
          {/* blog, topic and article pages come next; until then these show a friendly placeholder */}
          <Route path="/resources/*" element={<KcComingSoon />} />
          <Route path="*" element={<HomePage />} />
        </Routes>
      </main>
      <SiteFooter />
      <WorkModal />
      <Wizard />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <WizardProvider>
        <ModalProvider>
          <AppInner />
        </ModalProvider>
      </WizardProvider>
    </BrowserRouter>
  );
}

export default App;
