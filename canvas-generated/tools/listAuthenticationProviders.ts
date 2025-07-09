
import { tool } from "ai";
import { listAuthenticationProvidersDataSchema } from "./aitm.schema.ts";
import { listAuthenticationProviders, ListAuthenticationProvidersData } from "..";

export default tool({
  description: `
  List authentication providers
Returns a paginated list of authentication providers
    `,
  parameters: listAuthenticationProvidersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAuthenticationProvidersData, "url"> ) => {
    try {
      const { data } = await listAuthenticationProviders(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    