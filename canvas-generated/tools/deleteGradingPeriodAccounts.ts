
import { tool } from "ai";
import { deleteGradingPeriodAccountsDataSchema } from "./aitm.schema.ts";
import { deleteGradingPeriodAccounts, DeleteGradingPeriodAccountsData } from "..";

export default tool({
  description: `
  Delete a grading period
<b>204 No Content</b> response code is returned if the deletion
was
successful.
    `,
  parameters: deleteGradingPeriodAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteGradingPeriodAccountsData, "url"> ) => {
    try {
      const { data } = await deleteGradingPeriodAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    