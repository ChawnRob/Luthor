import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/contexts/AuthContext";
import { getApiUrl } from "@/lib/api";
import { Brain } from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "wouter";
import { toast } from "sonner";

export default function Login() {
  const { signIn } = useAuth();
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      await signIn(email, password);
      toast.success("Connexion réussie");
      setLocation("/");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Échec de connexion");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(0,217,255,0.18),transparent_40%),radial-gradient(circle_at_80%_0%,rgba(99,102,241,0.2),transparent_35%)]" />
      <Card className="relative z-10 w-full max-w-md border-primary/20 bg-card/80 backdrop-blur-xl">
        <CardHeader className="text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 text-primary">
            <Brain className="h-6 w-6" />
          </div>
          <CardTitle>Connexion LUTHOR</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={(e) => void handleSubmit(e)}>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Mot de passe</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              Se connecter
            </Button>
          </form>

          <div className="mt-4 grid gap-2">
            <Button variant="outline" asChild>
              <a href={`${getApiUrl()}/auth/oauth/google`}>Continuer avec Google</a>
            </Button>
            <Button variant="outline" asChild>
              <a href={`${getApiUrl()}/auth/oauth/apple`}>Continuer avec Apple</a>
            </Button>
          </div>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Pas de compte ?{" "}
            <Link href="/signup" className="text-primary hover:underline">
              Créer un compte
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
