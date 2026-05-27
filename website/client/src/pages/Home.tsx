import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ArrowRight, Zap, Brain, TrendingDown, Github } from "lucide-react";

export default function Home() {
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
            <a href="#features" className="text-sm hover:text-primary transition">Features</a>
            <a href="#architecture" className="text-sm hover:text-primary transition">Architecture</a>
            <a href="#pricing" className="text-sm hover:text-primary transition">Pricing</a>
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
            alt="Hero Background"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl">
            <div className="inline-block mb-6 px-4 py-2 bg-primary/10 border border-primary/30 rounded-full">
              <span className="text-primary text-sm font-medium">Agentic AI for Everyone</span>
            </div>
            <h1 className="text-6xl font-bold mb-6 leading-tight">
              The Future of <span className="text-primary">Intelligent Agents</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
              Luthor is an Agentic World Model powered by JEPA and Subquadratic architecture. 
              Build autonomous AI systems that think, plan, and act—without the massive costs of traditional LLMs.
            </p>
            <div className="flex gap-4">
              <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
                Get Started <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button size="lg" variant="outline" className="border-primary text-primary hover:bg-primary/10">
                Read Docs
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-card/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Why Luthor?</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              A revolutionary approach to agentic AI that combines cutting-edge research with practical efficiency.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <Card className="bg-background border-border p-8 hover:border-primary/50 transition">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Brain className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">JEPA Architecture</h3>
              <p className="text-muted-foreground">
                Learn abstract world representations without generating images. Predict the future in latent space for maximum efficiency.
              </p>
            </Card>

            {/* Feature 2 */}
            <Card className="bg-background border-border p-8 hover:border-primary/50 transition">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Subquadratic Scaling</h3>
              <p className="text-muted-foreground">
                Linear complexity instead of quadratic. Handle massive contexts (12M+ tokens) with minimal computational overhead.
              </p>
            </Card>

            {/* Feature 3 */}
            <Card className="bg-background border-border p-8 hover:border-primary/50 transition">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <TrendingDown className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">80% Cost Reduction</h3>
              <p className="text-muted-foreground">
                Enterprise-grade AI at SME prices. Luthor costs 5x less than Claude while delivering superior reasoning.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-muted-foreground text-lg">Three-stage pipeline for autonomous reasoning</p>
          </div>
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <img 
              src="https://d2xsxph8kpxj0f.cloudfront.net/310519663673037996/8bXeNzZyAW5sGEALmMumNx/luthor_architecture_diagram-Vp4WuY5nqsrtViincf9et2.webp"
              alt="Architecture Diagram"
              className="w-full"
            />
          </div>
          <div className="grid md:grid-cols-3 gap-8 mt-12">
            <div>
              <h3 className="text-primary font-bold mb-2">1. JEPA Encoder</h3>
              <p className="text-muted-foreground">Compress raw observations into abstract latent representations.</p>
            </div>
            <div>
              <h3 className="text-primary font-bold mb-2">2. Latent Predictor</h3>
              <p className="text-muted-foreground">Predict future states in the latent space using transformer dynamics.</p>
            </div>
            <div>
              <h3 className="text-primary font-bold mb-2">3. MPC Planner</h3>
              <p className="text-muted-foreground">Optimize action sequences to minimize cost and reach goals.</p>
            </div>
          </div>
        </div>
      </section>

      {/* JEPA Concept Section */}
      <section className="py-20 bg-card/50">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">Understanding JEPA</h2>
              <p className="text-muted-foreground mb-4">
                Joint Embedding Predictive Architecture (JEPA) is Yann LeCun's vision for the future of AI. 
                Instead of training models to generate pixels or tokens, JEPA learns to predict in an abstract space.
              </p>
              <p className="text-muted-foreground mb-4">
                This approach is fundamentally more efficient and aligns with how biological intelligence works—
                by building internal models of the world rather than memorizing patterns.
              </p>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Non-generative: Focus on what matters</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Energy-efficient: Minimal compute overhead</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Scalable: Works with massive datasets</span>
                </li>
              </ul>
            </div>
            <div className="bg-background border border-border rounded-lg overflow-hidden">
              <img 
                src="https://d2xsxph8kpxj0f.cloudfront.net/310519663673037996/8bXeNzZyAW5sGEALmMumNx/luthor_jepa_concept-QLkd4B9r5vfzpPmogeT8CA.webp"
                alt="JEPA Concept"
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
            <h2 className="text-4xl font-bold mb-4">Affordable Intelligence</h2>
            <p className="text-muted-foreground text-lg">Luthor delivers frontier-level AI at SME prices</p>
          </div>
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <img 
              src="https://d2xsxph8kpxj0f.cloudfront.net/310519663673037996/8bXeNzZyAW5sGEALmMumNx/luthor_cost_comparison-9ENEdNnPFuCRCidm8sMuQ8.webp"
              alt="Cost Comparison"
              className="w-full"
            />
          </div>
          <div className="mt-12 bg-primary/10 border border-primary/30 rounded-lg p-8">
            <h3 className="text-2xl font-bold mb-4">The Hybrid Strategy</h3>
            <p className="text-muted-foreground mb-6">
              For maximum ROI, combine Luthor with local Small Language Models (SLMs) and selective API calls:
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <div className="text-primary font-bold mb-2">Step 1: Local SLMs</div>
                <p className="text-sm text-muted-foreground">Run Llama 3 or Phi-3 locally for 90% of tasks. Cost: $0/month after hardware.</p>
              </div>
              <div>
                <div className="text-primary font-bold mb-2">Step 2: Luthor Orchestration</div>
                <p className="text-sm text-muted-foreground">Luthor decides when to call expensive APIs. Reduces cloud spend by 70-90%.</p>
              </div>
              <div>
                <div className="text-primary font-bold mb-2">Step 3: SubQ for Scale</div>
                <p className="text-sm text-muted-foreground">Use Subquadratic for massive contexts. 5x cheaper than Claude for long documents.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-card/50">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Build Autonomous AI?</h2>
          <p className="text-muted-foreground text-lg mb-8 max-w-2xl mx-auto">
            Join the revolution. Luthor is open-source and ready for production deployment.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
              Start Building <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
            <Button size="lg" variant="outline" className="border-primary text-primary hover:bg-primary/10">
              <Github className="w-4 h-4 mr-2" />
              View on GitHub
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
              <p className="text-sm text-muted-foreground">Agentic World Model for the future.</p>
            </div>
            <div>
              <h4 className="font-bold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-primary transition">Features</a></li>
                <li><a href="#" className="hover:text-primary transition">Pricing</a></li>
                <li><a href="#" className="hover:text-primary transition">Docs</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Community</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-primary transition">GitHub</a></li>
                <li><a href="#" className="hover:text-primary transition">Discord</a></li>
                <li><a href="#" className="hover:text-primary transition">Twitter</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-primary transition">Privacy</a></li>
                <li><a href="#" className="hover:text-primary transition">Terms</a></li>
                <li><a href="#" className="hover:text-primary transition">License</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border pt-8 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">© 2026 Luthor. Built by Manus AI.</p>
            <p className="text-sm text-muted-foreground">Inspired by Yann LeCun's AMI vision.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
