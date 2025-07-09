
import { tool } from "ai";
import { importOutcomesAccountsDataSchema } from "./aitm.schema.ts";
import { importOutcomesAccounts, ImportOutcomesAccountsData } from "..";

export default tool({
  description: `
  Import Outcomes
Import outcomes into Canvas.

For more information on the format that's expected
here, please see the
"Outcomes CSV" section in the API docs.
    `,
  parameters: importOutcomesAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ImportOutcomesAccountsData, "url"> ) => {
    try {
      const { data } = await importOutcomesAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    