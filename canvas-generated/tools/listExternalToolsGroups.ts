
import { tool } from "ai";
import { listExternalToolsGroupsDataSchema } from "./aitm.schema.ts";
import { listExternalToolsGroups, ListExternalToolsGroupsData } from "..";

export default tool({
  description: `
  List external tools
Returns the paginated list of external tools for the current context.
See the
get request docs for a single tool for a list of properties on an external tool.
    `,
  parameters: listExternalToolsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListExternalToolsGroupsData, "url"> ) => {
    try {
      const { data } = await listExternalToolsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    