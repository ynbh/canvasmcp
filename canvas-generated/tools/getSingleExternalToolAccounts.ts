
import { tool } from "ai";
import { getSingleExternalToolAccountsDataSchema } from "./aitm.schema.ts";
import { getSingleExternalToolAccounts, GetSingleExternalToolAccountsData } from "..";

export default tool({
  description: `
  Get a single external tool
Returns the specified external tool.
    `,
  parameters: getSingleExternalToolAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleExternalToolAccountsData, "url"> ) => {
    try {
      const { data } = await getSingleExternalToolAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    