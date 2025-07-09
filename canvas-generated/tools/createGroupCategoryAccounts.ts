
import { tool } from "ai";
import { createGroupCategoryAccountsDataSchema } from "./aitm.schema.ts";
import { createGroupCategoryAccounts, CreateGroupCategoryAccountsData } from "..";

export default tool({
  description: `
  Create a Group Category
Create a new group category
    `,
  parameters: createGroupCategoryAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateGroupCategoryAccountsData, "url"> ) => {
    try {
      const { data } = await createGroupCategoryAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    