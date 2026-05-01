import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from "@tanstack/react-query";

import api from "@/lib/api";

type ApiKey = readonly unknown[];

export const useApiQuery = <T>(
  key: ApiKey,
  url: string,
  options?: Omit<UseQueryOptions<T>, "queryKey" | "queryFn">,
) =>
  useQuery<T>({
    queryKey: key,
    queryFn: async () => {
      const r = await api.get<T>(url);
      return r.data;
    },
    ...options,
  });

export const useApiMutation = <Req, Res>(
  url: string | ((req: Req) => string),
  method: "post" | "patch" | "put" | "delete" = "post",
  options?: UseMutationOptions<Res, Error, Req>,
) =>
  useMutation<Res, Error, Req>({
    mutationFn: async (req) => {
      const target = typeof url === "function" ? url(req) : url;
      const r = await api.request<Res>({
        url: target,
        method,
        data: method === "delete" ? undefined : req,
      });
      return r.data;
    },
    ...options,
  });
