
import { tool } from "ai";
import { listLinkedOutcomesAccountsDataSchema } from "./aitm.schema.ts";
import { listLinkedOutcomesAccounts, ListLinkedOutcomesAccountsData } from "..";

export default tool({
  description: `
  List linked outcomes
A paginated list of the immediate OutcomeLink children of the outcome group.
    `,
  parameters: listLinkedOutcomesAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListLinkedOutcomesAccountsData, "url"> ) => {
    try {
      const { data } = await listLinkedOutcomesAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    