
import { tool } from "ai";
import { createModuleDataSchema } from "./aitm.schema.ts";
import { createModule, CreateModuleData } from "..";

export default tool({
  description: `
  Create a module
Create and return a new module
    `,
  parameters: createModuleDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateModuleData, "url"> ) => {
    try {
      const { data } = await createModule(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    