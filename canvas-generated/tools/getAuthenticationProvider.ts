
import { tool } from "ai";
import { getAuthenticationProviderDataSchema } from "./aitm.schema.ts";
import { getAuthenticationProvider, GetAuthenticationProviderData } from "..";

export default tool({
  description: `
  Get authentication provider
Get the specified authentication provider
    `,
  parameters: getAuthenticationProviderDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAuthenticationProviderData, "url"> ) => {
    try {
      const { data } = await getAuthenticationProvider(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    