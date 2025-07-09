
import { tool } from "ai";
import { queryByAccountDataSchema } from "./aitm.schema.ts";
import { queryByAccount, QueryByAccountData } from "..";

export default tool({
  description: `
  Query by account.
List authentication events for a given account.
    `,
  parameters: queryByAccountDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryByAccountData, "url"> ) => {
    try {
      const { data } = await queryByAccount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    