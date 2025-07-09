
import { tool } from "ai";
import { createExternalToolAccountsDataSchema } from "./aitm.schema.ts";
import { createExternalToolAccounts, CreateExternalToolAccountsData } from "..";

export default tool({
  description: `
  Create an external tool
Create an external tool in the specified course/account.
The created tool
will be returned, see the "show" endpoint for an example.
    `,
  parameters: createExternalToolAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateExternalToolAccountsData, "url"> ) => {
    try {
      const { data } = await createExternalToolAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    