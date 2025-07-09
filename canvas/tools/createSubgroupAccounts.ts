
import { tool } from "ai";
import { createSubgroupAccountsDataSchema } from "./aitm.schema.ts";
import { createSubgroupAccounts, CreateSubgroupAccountsData } from "..";

export default tool({
  description: `
  Create a subgroup
Creates a new empty subgroup under the outcome group with the given title
and
description.
    `,
  parameters: createSubgroupAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateSubgroupAccountsData, "url"> ) => {
    try {
      const { data } = await createSubgroupAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    