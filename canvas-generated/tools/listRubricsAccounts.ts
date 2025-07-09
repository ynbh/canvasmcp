
import { tool } from "ai";
import { listRubricsAccountsDataSchema } from "./aitm.schema.ts";
import { listRubricsAccounts, ListRubricsAccountsData } from "..";

export default tool({
  description: `
  List rubrics
Returns the paginated list of active rubrics for the current context.
    `,
  parameters: listRubricsAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListRubricsAccountsData, "url"> ) => {
    try {
      const { data } = await listRubricsAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    