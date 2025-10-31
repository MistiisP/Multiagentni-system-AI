import React from 'react';
import { Link } from 'react-router-dom';
import '../css/Home.css';

const About: React.FC = () => {
  return (
    <div className="home-container">
      <section className="hero-section">
        <h1>Multi-Agent Systém</h1>
        <p className="subtitle">
          Inteligentní platforma pro vytváření a správu AI agentů s vizuálním editorem workflow
        </p>
      </section>

      <section className="features-section">
        <div className="feature-card">
          <i className='bx bx-bot'></i>
          <h3>Inteligentní Agenti</h3>
          <p>
            Vytvářejte vlastní AI agenty s různými rolemi a schopnostmi. Každý agent může mít své vlastní nástroje, 
            promptové instrukce a je napojen na pokročilé jazykové modely jako GPT-4, Claude nebo vlastní LLM.
          </p>
        </div>

        <div className="feature-card">
          <i className='bx bx-network-chart'></i>
          <h3>Vizuální Workflow Editor</h3>
          <p>
            Pomocí drag-and-drop rozhraní můžete vytvářet komplexní grafy workflow, kde uzly reprezentují agenty 
            a hrany definují přechody mezi nimi. Manager agent koordinuje práci specialistů a deleguje úkoly 
            podle potřeby.
          </p>
        </div>

        <div className="feature-card">
          <i className='bx bx-conversation'></i>
          <h3>Chatovací Rozhraní</h3>
          <p>
            Komunikujte s vašimi agenty přes intuitivní chat. Sledujte v reálném čase, jak manager analyzuje 
            váš požadavek, deleguje úkoly specialistům a shromažďuje výsledky. Veškerá konverzace je uložena 
            pro pozdější analýzu.
          </p>
        </div>

        <div className="feature-card">
          <i className='bx bx-data'></i>
          <h3>Analytika & Historie</h3>
          <p>
            Získejte přehled o využití agentů, spotřebě tokenů a úspěšnosti jednotlivých workflow. 
            Prohlížejte si historii spuštění grafů včetně detailního logu každého kroku a přechodů mezi agenty.
          </p>
        </div>
      </section>

      <section className="tech-section">
        <h2>Technologie</h2>
        <div className="tech-stack">
          <div className="tech-item">
            <h4>Backend</h4>
            <ul>
              <li><strong>FastAPI</strong> – moderní Python framework pro API</li>
              <li><strong>LangChain & LangGraph</strong> – workflow AI agentů</li>
              <li><strong>PostgreSQL</strong> – databáze s asynchronním přístupem</li>
              <li><strong>WebSockets</strong> – real-time komunikace</li>
            </ul>
          </div>
          <div className="tech-item">
            <h4>Frontend</h4>
            <ul>
              <li><strong>React + TypeScript</strong> – moderní UI framework</li>
              <li><strong>Vite</strong> – rychlý build tool</li>
              <li><strong>React Flow</strong> – vizualizace grafů</li>
              <li><strong>Context API</strong> – stavový management</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <h2>Jak to funguje?</h2>
        <div className="workflow-steps">
          <div className="step">
            <span className="step-number">1</span>
            <h4>Vytvoř agenty</h4>
            <p>Definuj role, nástroje a AI modely pro své agenty</p>
          </div>
          <div className="step">
            <span className="step-number">2</span>
            <h4>Spusť chat</h4>
            <p>Vytvoř chat a přiřaď agenty</p>
          </div>
          <div className="step">
            <span className="step-number">3</span>
            <h4>Sestav graf</h4>
            <p>Vizuálně propoj agenty do workflow grafu</p>
          </div>
          <div className="step">
            <span className="step-number">4</span>
            <h4>Ptej se</h4>
            <p>Komunikuj s managerem a sleduj, jak deleguje úkoly</p>
          </div>
          <div className="step">
            <span className="step-number">5</span>
            <h4>Analyzuj výsledky</h4>
            <p>Prohlížej statistiky, logy a historii spuštění</p>
          </div>
        </div>
      </section>

      <section className="use-cases">
        <h2>Případy použití</h2>
        <ul className="use-case-list">
          <li>📊 <strong>Automatizace analýzy dat</strong> – Agenti mohou zpracovávat data, provádět výpočty a generovat reporty</li>
          <li>🔍 <strong>Výzkum a web scraping</strong> – Specializovaní agenti mohou vyhledávat informace a extrahovat data z webu</li>
          <li>✍️ <strong>Generování obsahu</strong> – Koordinace psaní článků, kódu, dokumentace napříč více AI modely</li>
          <li>🤖 <strong>Zákaznická podpora</strong> – Multi-level podpora s eskalací mezi specializovanými agenty</li>
          <li>🧪 <strong>Výzkum a vývoj</strong> – Experimenty s různými AI architekturami a workflow</li>
        </ul>
      </section>

      <section className="cta-section">
        <h2>Začněte ještě dnes</h2>
        <p>Zaregistrujte se a vytvořte svůj první multi-agentní systém za pár minut</p>
        <a href="/signup" className="cta-button">Vytvořit účet</a>
        <br />
        <Link to="/home" className="cta-button" style={{ marginTop: 20, background: "#fff", color: "#667eea" }}>
          Zpět na hlavní stránku
        </Link>
      </section>
    </div>
  );
};

export default About;