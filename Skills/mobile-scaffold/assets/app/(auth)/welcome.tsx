import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { Screen } from "@/components/pages/screen";
import { useToster } from "@/components/ui/toster";
import { requestOTP } from "@/services/actions/auth_actions";
import { getErrorMessage } from "@/libs/utils";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { KeyboardAvoidingView, Platform, ScrollView, Text, View } from "react-native";
import { z } from "zod";

const welcomeSchema = z.object({
  identifier: z.string().min(1, "Enter your phone number or email"),
});
type WelcomeInput = z.infer<typeof welcomeSchema>;

export default function WelcomeScreen() {
  const { show } = useToster();
  const form = useForm<WelcomeInput>({
    resolver: zodResolver(welcomeSchema),
    defaultValues: { identifier: "" },
    mode: "onChange",
  });

  const mutation = useMutation({
    mutationFn: (values: WelcomeInput) => requestOTP(values.identifier),
    onSuccess: () => show({ type: "success", message: "Code sent." }),
    onError: (error) => show({ type: "error", message: getErrorMessage(error) }),
  });

  return (
    <Screen>
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
        <ScrollView contentContainerClassName="flex-1 justify-center px-6" keyboardShouldPersistTaps="handled">
          <Text className="mb-2 text-center text-[28px] font-bold text-ink-900">Welcome</Text>
          <Text className="mb-8 text-center text-[14px] text-ink-500">
            Enter your phone number or email to get started.
          </Text>

          <View className="gap-4">
            <TextField control={form.control} name="identifier" label="Phone or email" keyboardType="default" />
            <Button
              label="Continue"
              onPress={form.handleSubmit((values) => mutation.mutate(values))}
              loading={mutation.isPending}
              disabled={!form.formState.isValid}
            />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </Screen>
  );
}
