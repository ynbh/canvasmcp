
import { tool } from "ai";
import { updateAuthenticationProviderDataSchema } from "./aitm.schema.ts";
import { updateAuthenticationProvider, UpdateAuthenticationProviderData } from "..";

export default tool({
  description: `
  Update authentication provider
Update an authentication provider using the same options as the
create endpoint.
You can not update an existing provider to a new authentication type.
    `,
  parameters: updateAuthenticationProviderDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateAuthenticationProviderData, "url"> ) => {
    try {
      const { data } = await updateAuthenticationProvider(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    