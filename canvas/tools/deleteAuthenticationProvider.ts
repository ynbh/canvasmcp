
import { tool } from "ai";
import { deleteAuthenticationProviderDataSchema } from "./aitm.schema.ts";
import { deleteAuthenticationProvider, DeleteAuthenticationProviderData } from "..";

export default tool({
  description: `
  Delete authentication provider
Delete the config
    `,
  parameters: deleteAuthenticationProviderDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteAuthenticationProviderData, "url"> ) => {
    try {
      const { data } = await deleteAuthenticationProvider(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    