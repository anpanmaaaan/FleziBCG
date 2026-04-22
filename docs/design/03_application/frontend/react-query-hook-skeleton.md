# REACT QUERY HOOK SKELETON

import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/app/api/client";

export function useStartOperation() {
  return useMutation({
    mutationFn: async ({ opId, payload }) => {
      const res = await apiClient.post(`/execution/${opId}/start`, payload);
      return res.data;
    }
  });
}
