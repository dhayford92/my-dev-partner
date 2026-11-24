import { Screen } from "@/components/pages/screen";
import { ErrorState } from "@/components/ui/states";
import { Skeleton } from "@/components/ui/skeleton";
import { queryKeys } from "@/libs/query_keys";
import { getErrorMessage } from "@/libs/utils";
import { getMe } from "@/services/actions/profile_actions";
import { useQuery } from "@tanstack/react-query";
import { Text, View } from "react-native";

/**
 * Home shell + first-run smoke test: renders, then makes one authenticated request and
 * surfaces loading/error/data using the shared primitives.
 */
export default function HomeScreen() {
  const meQuery = useQuery({
    queryKey: queryKeys.profile.me(),
    queryFn: getMe,
    retry: false,
  });

  return (
    <Screen>
      <View className="flex-1 px-5 pt-6">
        <Text className="text-[24px] font-bold text-ink-900">Welcome</Text>
        <Text className="mt-1 text-[14px] text-ink-500">Your authenticated shell is rendering.</Text>

        <View className="mt-6 rounded-2xl border border-ink-200 p-5">
          <Text className="mb-3 text-[13px] font-semibold text-ink-700">Backend connection</Text>
          {meQuery.isLoading ? (
            <View className="gap-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </View>
          ) : meQuery.isError ? (
            <ErrorState message={getErrorMessage(meQuery.error)} retry={() => meQuery.refetch()} />
          ) : (
            <Text className="text-[12px] text-ink-500">{JSON.stringify(meQuery.data, null, 2)}</Text>
          )}
        </View>
      </View>
    </Screen>
  );
}
