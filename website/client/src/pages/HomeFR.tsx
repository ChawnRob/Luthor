import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ArrowRight, Zap, Brain, TrendingDown, Github } from "lucide-react";

export default function HomeFR() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-background/80 backdrop-blur-md border-b border-border z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold">L</span>
            </div>
            <span className="text-xl font-bold">Luthor</span>
          </div>
          <div className="flex items-center gap-6">
            <a href="#features" className="text-sm hover:text-primary transition">Fonctionnalités</a>
            <a href="#architecture" className="text-sm hover:text-primary transition">Architecture</a>
            <a href="#pricing" className="text-sm hover:text-primary transition">Tarification</a>
            <div className="flex gap-2">
              <a href="/en" className="text-xs px-2 py-1 hover:text-primary transition">EN</a>
              <span className="text-xs text-primary">FR</span>
            </div>
            <Button variant="outline" size="sm" className="border-primary text-primary hover:bg-primary/10">
              <Github className="w-4 h-4 mr-2" />
              GitHub
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 relative overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <img 
            src="https://d2xsxph8kpxj0f.cloudfront.net/310519663673037996/8bXeNzZyAW5sGEALmMumNx/luthor_hero_background-UDXh8kd7663fm5X3ojVf7W.webp"
            alt="Arrière-plan Hero"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl">
            <div className="inline-block mb-6 px-4 py-2 bg-primary/10 border border-primary/30 rounded-full">
              <span className="text-primary text-sm font-medium">L'IA Agentique pour Tous</span>
            </div>
            <h1 className="text-6xl font-bold mb-6 leading-tight">
              L'Avenir des <span className="text-primary">Agents Intelligents</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
              Luthor est un Modèle de Monde Agentique alimenté par l'architecture JEPA de Yann LeCun et la technologie Subquadratique. 
              Construisez des systèmes d'IA autonomes qui pensent, planifient et agissent—sans les coûts massifs des LLM traditionnels.
            </p>
            <div className="flex gap-4">
              <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
                Commencer <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button size="lg" variant="outline" className="border-primary text-primary hover:bg-primary/10">
                Lire la Documentation
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-card/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Pourquoi Luthor ?</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Une approche révolutionnaire de l'IA agentique qui combine la recherche de pointe avec une efficacité pratique.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <Card className="bg-background border-border p-8 hover:border-primary/50 transition">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Brain className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Architecture JEPA</h3>
              <p className="text-muted-foreground">
                Apprenez des représentations abstraites du monde sans générer d'images. Prédisez l'avenir dans l'espace latent pour une efficacité maximale.
              </p>
            </Card>

            {/* Feature 2 */}
            <Card className="bg-background border-border p-8 hover:border-primary/50 transition">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Mise à l'Échelle Subquadratique</h3>
              <p className="text-muted-foreground">
                Complexité linéaire au lieu de quadratique. Gérez des contextes massifs (12M+ tokens) avec un surcoût computationnel minimal.
              </p>
            </Card>

            {/* Feature 3 */}
            <Card className="bg-background border-border p-8 hover:border-primary/50 transition">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <TrendingDown className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Réduction de 80% des Coûts</h3>
              <p className="text-muted-foreground">
                L'IA de niveau entreprise à des prix PME. Luthor coûte 5 fois moins cher que Claude tout en offrant un raisonnement supérieur.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Comment Ça Marche</h2>
            <p className="text-muted-foreground text-lg">Pipeline à trois étapes pour le raisonnement autonome</p>
          </div>
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <img 
              src="https://d2xsxph8kpxj0f.cloudfront.net/310519663673037996/8bXeNzZyAW5sGEALmMumNx/luthor_architecture_diagram-Vp4WuY5nqsrtViincf9et2.webp"
              alt="Diagramme d'Architecture"
              className="w-full"
            />
          </div>
          <div className="grid md:grid-cols-3 gap-8 mt-12">
            <div>
              <h3 className="text-primary font-bold mb-2">1. Encodeur JEPA</h3>
              <p className="text-muted-foreground">Compressez les observations brutes en représentations latentes abstraites.</p>
            </div>
            <div>
              <h3 className="text-primary font-bold mb-2">2. Prédicteur Latent</h3>
              <p className="text-muted-foreground">Prédisez les états futurs dans l'espace latent en utilisant la dynamique des transformers.</p>
            </div>
            <div>
              <h3 className="text-primary font-bold mb-2">3. Planificateur MPC</h3>
              <p className="text-muted-foreground">Optimisez les séquences d'actions pour minimiser les coûts et atteindre les objectifs.</p>
            </div>
          </div>
        </div>
      </section>

      {/* JEPA Concept Section */}
      <section className="py-20 bg-card/50">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">Comprendre JEPA</h2>
              <p className="text-muted-foreground mb-4">
                L'Architecture de Prédiction d'Intégration Conjointe (JEPA) est la vision de Yann LeCun pour l'avenir de l'IA. 
                Au lieu d'entraîner des modèles à générer des pixels ou des tokens, JEPA apprend à prédire dans un espace abstrait.
              </p>
              <p className="text-muted-foreground mb-4">
                Cette approche est fondamentalement plus efficace et s'aligne sur la façon dont l'intelligence biologique fonctionne—
                en construisant des modèles internes du monde plutôt qu'en mémorisant des motifs.
              </p>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Non-génératif : Concentrez-vous sur ce qui compte</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Efficace énergétiquement : Surcoût computationnel minimal</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Scalable : Fonctionne avec des datasets massifs</span>
                </li>
              </ul>
            </div>
            <div className="bg-background border border-border rounded-lg overflow-hidden">
              <img 
                src="https://d2xsxph8kpxj0f.cloudfront.net/310519663673037996/8bXeNzZyAW5sGEALmMumNx/luthor_jepa_concept-QLkd4B9r5vfzpPmogeT8CA.webp"
                alt="Concept JEPA"
                className="w-full"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Cost Comparison Section */}
      <section id="pricing" className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">L'Intelligence Abordable</h2>
            <p className="text-muted-foreground text-lg">Luthor offre une IA de niveau frontier à des prix PME</p>
          </div>
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <img 
              src="https://d2xsxph8kpxj0f.cloudfront.net/310519663673037996/8bXeNzZyAW5sGEALmMumNx/luthor_cost_comparison-9ENEdNnPFuCRCidm8sMuQ8.webp"
              alt="Comparaison des Coûts"
              className="w-full"
            />
          </div>
          <div className="mt-12 bg-primary/10 border border-primary/30 rounded-lg p-8">
            <h3 className="text-2xl font-bold mb-4">La Stratégie Hybride</h3>
            <p className="text-muted-foreground mb-6">
              Pour un ROI maximal, combinez Luthor avec des Small Language Models (SLM) locaux et des appels API sélectifs :
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <div className="text-primary font-bold mb-2">Étape 1 : SLM Locaux</div>
                <p className="text-sm text-muted-foreground">Exécutez Llama 3 ou Phi-3 localement pour 90% des tâches. Coût : 0€/mois après matériel.</p>
              </div>
              <div>
                <div className="text-primary font-bold mb-2">Étape 2 : Orchestration Luthor</div>
                <p className="text-sm text-muted-foreground">Luthor décide quand appeler les API coûteuses. Réduit les dépenses cloud de 70-90%.</p>
              </div>
              <div>
                <div className="text-primary font-bold mb-2">Étape 3 : SubQ pour l'Échelle</div>
                <p className="text-sm text-muted-foreground">Utilisez Subquadratic pour les contextes massifs. 5x moins cher que Claude pour les longs documents.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-card/50">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Prêt à Construire une IA Autonome ?</h2>
          <p className="text-muted-foreground text-lg mb-8 max-w-2xl mx-auto">
            Rejoignez la révolution. Luthor est open-source et prêt pour le déploiement en production.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
              Commencer à Construire <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
            <Button size="lg" variant="outline" className="border-primary text-primary hover:bg-primary/10">
              <Github className="w-4 h-4 mr-2" />
              Voir sur GitHub
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 bg-background">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <span className="text-primary-foreground font-bold">L</span>
                </div>
                <span className="font-bold">Luthor</span>
              </div>
              <p className="text-sm text-muted-foreground">Modèle de Monde Agentique pour l'avenir.</p>
            </div>
            <div>
              <h4 className="font-bold mb-4">Produit</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-primary transition">Fonctionnalités</a></li>
                <li><a href="#" className="hover:text-primary transition">Tarification</a></li>
                <li><a href="#" className="hover:text-primary transition">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Communauté</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-primary transition">GitHub</a></li>
                <li><a href="#" className="hover:text-primary transition">Discord</a></li>
                <li><a href="#" className="hover:text-primary transition">Twitter</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Légal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-primary transition">Confidentialité</a></li>
                <li><a href="#" className="hover:text-primary transition">Conditions</a></li>
                <li><a href="#" className="hover:text-primary transition">Licence</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border pt-8 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">© 2026 Luthor. Construit par Manus AI.</p>
            <p className="text-sm text-muted-foreground">Inspiré par la vision AMI de Yann LeCun.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
