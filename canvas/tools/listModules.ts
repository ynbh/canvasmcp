
import { tool } from "ai";
import { listModulesDataSchema } from "./aitm.schema.ts";
import { listModules, ListModulesData } from "..";

export default tool({
  description: `
  List modules
A paginated list of the modules in a course
    `,
  parameters: listModulesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListModulesData, "url"> ) => {
    try {
      const { data } = await listModules(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    