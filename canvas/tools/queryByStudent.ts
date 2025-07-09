
import { tool } from "ai";
import { queryByStudentDataSchema } from "./aitm.schema.ts";
import { queryByStudent, QueryByStudentData } from "..";

export default tool({
  description: `
  Query by student.
List grade change events for a given student.
    `,
  parameters: queryByStudentDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryByStudentData, "url"> ) => {
    try {
      const { data } = await queryByStudent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    