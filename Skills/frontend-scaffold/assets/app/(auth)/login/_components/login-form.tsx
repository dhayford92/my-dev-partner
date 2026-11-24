"use client";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import InputField from "@/components/custom/common/input-field";
import { loginAction } from "@/lib/actions/auth";

const loginSchema = z.object({
  email: z.string().email({ message: "Invalid email address" }),
  password: z.string().min(1, "Password is required"),
});
type LoginInput = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const form = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const mutation = useMutation({
    mutationFn: (data: LoginInput) => loginAction(data),
    onSuccess: (result) => {
      if (result.error) {
        toast.error(result.error);
        return;
      }
      toast.success("Signed in. Redirecting...");
      router.push("/portal");
    },
  });

  return (
    <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))} className="flex flex-col gap-4">
      <div className="flex flex-col items-center gap-1 text-center">
        <h1 className="text-2xl font-bold">Login to your account</h1>
        <p className="text-muted-foreground text-sm">Enter your email below to sign in</p>
      </div>

      <InputField control={form.control} name="email" label="Email" placeholder="m@example.com" disabled={mutation.isPending} />
      <InputField control={form.control} name="password" label="Password" type="password" disabled={mutation.isPending} />

      <Button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "Signing in..." : "Login"}
      </Button>
    </form>
  );
}
