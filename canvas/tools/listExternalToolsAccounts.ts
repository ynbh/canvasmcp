
import { tool } from "ai";
import { listExternalToolsAccountsDataSchema } from "./aitm.schema.ts";
import { listExternalToolsAccounts, ListExternalToolsAccountsData } from "..";

export default tool({
  description: `
  List external tools
Returns the paginated list of external tools for the current context.
See the
get request docs for a single tool for a list of properties on an external tool.
    `,
  parameters: listExternalToolsAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListExternalToolsAccountsData, "url"> ) => {
    try {
      const { data } = await listExternalToolsAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    