
import { tool } from "ai";
import { getSessionlessLaunchUrlForExternalToolAccountsDataSchema } from "./aitm.schema.ts";
import { getSessionlessLaunchUrlForExternalToolAccounts, GetSessionlessLaunchUrlForExternalToolAccountsData } from "..";

export default tool({
  description: `
  Get a sessionless launch url for an external tool.
Returns a sessionless launch url for an external
tool.

NOTE: Either the id or url must be provided unless launch_type is assessment or module_item.
    `,
  parameters: getSessionlessLaunchUrlForExternalToolAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSessionlessLaunchUrlForExternalToolAccountsData, "url"> ) => {
    try {
      const { data } = await getSessionlessLaunchUrlForExternalToolAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    