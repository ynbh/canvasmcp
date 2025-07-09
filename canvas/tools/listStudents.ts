
import { tool } from "ai";
import { listStudentsDataSchema } from "./aitm.schema.ts";
import { listStudents, ListStudentsData } from "..";

export default tool({
  description: `
  
    `,
  parameters: listStudentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListStudentsData, "url"> ) => {
    try {
      const { data } = await listStudents(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    