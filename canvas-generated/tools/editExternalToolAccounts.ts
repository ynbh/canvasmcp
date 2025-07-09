
import { tool } from "ai";
import { editExternalToolAccountsDataSchema } from "./aitm.schema.ts";
import { editExternalToolAccounts, EditExternalToolAccountsData } from "..";

export default tool({
  description: `
  Edit an external tool
Update the specified external tool. Uses same parameters as create
    `,
  parameters: editExternalToolAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditExternalToolAccountsData, "url"> ) => {
    try {
      const { data } = await editExternalToolAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    