
import { tool } from "ai";
import { deleteExternalToolAccountsDataSchema } from "./aitm.schema.ts";
import { deleteExternalToolAccounts, DeleteExternalToolAccountsData } from "..";

export default tool({
  description: `
  Delete an external tool
Remove the specified external tool
    `,
  parameters: deleteExternalToolAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteExternalToolAccountsData, "url"> ) => {
    try {
      const { data } = await deleteExternalToolAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    