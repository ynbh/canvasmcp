
import { tool } from "ai";
import { showOutcomeGroupAccountsDataSchema } from "./aitm.schema.ts";
import { showOutcomeGroupAccounts, ShowOutcomeGroupAccountsData } from "..";

export default tool({
  description: `
  Show an outcome group
    `,
  parameters: showOutcomeGroupAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowOutcomeGroupAccountsData, "url"> ) => {
    try {
      const { data } = await showOutcomeGroupAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    