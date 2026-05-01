import { ApolloClient, InMemoryCache, HttpLink, split } from "@apollo/client";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { getMainDefinition } from "@apollo/client/utilities";
import { createClient } from "graphql-ws";

import { useAuthStore } from "@/store/auth";

const httpLink = new HttpLink({
  uri: "/graphql",
  fetch: (uri, init) => {
    const token = useAuthStore.getState().token;
    const headers = new Headers(init?.headers);
    if (token) headers.set("Authorization", `Bearer ${token}`);
    return fetch(uri, { ...init, headers });
  },
});

const wsLink = new GraphQLWsLink(
  createClient({
    url: () => {
      const token = useAuthStore.getState().token;
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      return `${proto}//${window.location.host}/graphql${token ? `?token=${token}` : ""}`;
    },
  }),
);

const splitLink = split(
  ({ query }) => {
    const def = getMainDefinition(query);
    return def.kind === "OperationDefinition" && def.operation === "subscription";
  },
  wsLink,
  httpLink,
);

export const apolloClient = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});
