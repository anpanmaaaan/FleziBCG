# FRONTEND COMPONENT SKELETON

import { Button } from "@/components/ui/button";
import { useStartOperation } from "@/app/api/hooks";

export function StartButton({ opId }) {
  const mutation = useStartOperation();

  return (
    <Button
      onClick={() => mutation.mutate({ opId })}
      disabled={mutation.isPending}
    >
      Start
    </Button>
  );
}
