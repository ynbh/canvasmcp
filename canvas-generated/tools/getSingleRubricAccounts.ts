
import { tool } from "ai";
import { getSingleRubricAccountsDataSchema } from "./aitm.schema.ts";
import { getSingleRubricAccounts, GetSingleRubricAccountsData } from "..";

export default tool({
  description: `
  Get a single rubric
Returns the rubric with the given id.
    `,
  parameters: getSingleRubricAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleRubricAccountsData, "url"> ) => {
    try {
      const { data } = await getSingleRubricAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    