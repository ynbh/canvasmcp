
import { tool } from "ai";
import { bulkUpdateColumnDataDataSchema } from "./aitm.schema.ts";
import { bulkUpdateColumnData, BulkUpdateColumnDataData } from "..";

export default tool({
  description: `
  Bulk update column data
Set the content of custom columns

{
"column_data": [
{
"column_id":
example_column_id,
"user_id": example_student_id,
"content": example_content
},
{
"column_id":
example_column_id,
"user_id": example_student_id,
"content: example_content
}
]
}
    `,
  parameters: bulkUpdateColumnDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<BulkUpdateColumnDataData, "url"> ) => {
    try {
      const { data } = await bulkUpdateColumnData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    