
import { tool } from "ai";
import { listSubgroupsGlobalDataSchema } from "./aitm.schema.ts";
import { listSubgroupsGlobal, ListSubgroupsGlobalData } from "..";

export default tool({
  description: `
  List subgroups
A paginated list of the immediate OutcomeGroup children of the outcome group.
    `,
  parameters: listSubgroupsGlobalDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListSubgroupsGlobalData, "url"> ) => {
    try {
      const { data } = await listSubgroupsGlobal(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    