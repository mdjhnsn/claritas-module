# Copyright 2016 Google Inc. All Rights Reserved. Licensed under the Apache
# License, Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""Define a Wide + Deep model for classification on structured data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import multiprocessing

import six
import tensorflow as tf


# Define the format of your input data including unused columns
CSV_COLUMNS = [
'College',
'Prs_Blw_Pov_Lev',
'MrdCple_Fmly_HHD',
'NonFamily_HHD',
'Sngl_Prns_HHD',
'Rel_Child_Under_6',
'Med_HHD_Inc_BG',
'Med_HHD_Inc_TR',
'Renter_Occp_HU',
'Owner_Occp_HU',
'Single_Unit',
'MLT_U2_9_STRC',
'MLT_U10p',
'Med_House_Value_BG',
'One_Health_Ins',
'Two_Plus_Health_Ins',
'No_Health_Ins',
'Big_Sky_Families']

CSV_COLUMN_DEFAULTS = [[0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], ['']]
LABEL_COLUMN = 'Big_Sky_Families'
LABELS = ['No', 'Yes']

# Define the initial ingestion of each feature used by your model.
# Additionally, provide metadata about the feature.
INPUT_COLUMNS = [
   tf.feature_column.numeric_column('College'),
   tf.feature_column.numeric_column('Prs_Blw_Pov_Lev'),
   tf.feature_column.numeric_column('MrdCple_Fmly_HHD'),
   tf.feature_column.numeric_column('NonFamily_HHD'),
   tf.feature_column.numeric_column('Sngl_Prns_HHD'),
   tf.feature_column.numeric_column('Rel_Child_Under_6'),
   tf.feature_column.numeric_column('Med_HHD_Inc_BG'),
   tf.feature_column.numeric_column('Med_HHD_Inc_TR'),
   tf.feature_column.numeric_column('Renter_Occp_HU'),
   tf.feature_column.numeric_column('Owner_Occp_HU'),
   tf.feature_column.numeric_column('Single_Unit'),
   tf.feature_column.numeric_column('MLT_U2_9_STRC'),
   tf.feature_column.numeric_column('MLT_U10p'),
   tf.feature_column.numeric_column('Med_House_Value_BG'),
   tf.feature_column.numeric_column('One_Health_Ins'),
   tf.feature_column.numeric_column('Two_Plus_Health_Ins'),
   tf.feature_column.numeric_column('No_Health_Ins')
   ]

UNUSED_COLUMNS = set(CSV_COLUMNS) - {col.name for col in INPUT_COLUMNS} - {LABEL_COLUMN}

def build_estimator(config, embedding_size=8, hidden_units=None):
  (
    College,
    Prs_Blw_Pov_Lev,
    MrdCple_Fmly_HHD,
    NonFamily_HHD,
    Sngl_Prns_HHD,
    Rel_Child_Under_6,
    Med_HHD_Inc_BG,
    Med_HHD_Inc_TR,
    Renter_Occp_HU,
    Owner_Occp_HU,
    Single_Unit,
    MLT_U2_9_STRC,
    MLT_U10p,
    Med_House_Value_BG,
    One_Health_Ins,
    Two_Plus_Health_Ins,
    No_Health_Ins
    ) = INPUT_COLUMNS
  

  # Wide columns and deep columns.
  wide_columns = [
  College,
  Prs_Blw_Pov_Lev,
  MrdCple_Fmly_HHD,
  NonFamily_HHD,
  Sngl_Prns_HHD,
  Rel_Child_Under_6,
  Med_HHD_Inc_BG,
  Med_HHD_Inc_TR,
  Renter_Occp_HU,
  Owner_Occp_HU,
  Single_Unit,
  MLT_U2_9_STRC,
  MLT_U10p,
  Med_House_Value_BG,
  One_Health_Ins,
  Two_Plus_Health_Ins,
  No_Health_Ins
  ]

  deep_columns = [
  College,
  Prs_Blw_Pov_Lev,
  MrdCple_Fmly_HHD,
  NonFamily_HHD,
  Sngl_Prns_HHD,
  Rel_Child_Under_6,
  Med_HHD_Inc_BG,
  Med_HHD_Inc_TR,
  Renter_Occp_HU,
  Owner_Occp_HU,
  Single_Unit,
  MLT_U2_9_STRC,
  MLT_U10p,
  Med_House_Value_BG,
  One_Health_Ins,
  Two_Plus_Health_Ins,
  No_Health_Ins
  ]

  return tf.estimator.DNNLinearCombinedClassifier(
      config=config,
      linear_feature_columns=wide_columns,
      dnn_feature_columns=deep_columns,
      dnn_hidden_units=hidden_units or [100, 70, 50, 25]
  )


def parse_label_column(label_string_tensor):
  """Parses a string tensor into the label tensor
  Args:
    label_string_tensor: Tensor of dtype string. Result of parsing the
    CSV column specified by LABEL_COLUMN
  Returns:
    A Tensor of the same shape as label_string_tensor, should return
    an int64 Tensor representing the label index for classification tasks,
    and a float32 Tensor representing the value for a regression task.
  """
  # Build a Hash Table inside the graph
  table = tf.contrib.lookup.index_table_from_tensor(tf.constant(LABELS))

  # Use the hash table to convert string labels to ints and one-hot encode
  return table.lookup(label_string_tensor)


# ************************************************************************
# YOU NEED NOT MODIFY ANYTHING BELOW HERE TO ADAPT THIS MODEL TO YOUR DATA
# ************************************************************************


def csv_serving_input_fn():
  """Build the serving inputs."""
  csv_row = tf.placeholder(
      shape=[None],
      dtype=tf.string
  )
  features = parse_csv(csv_row)
  features.pop(LABEL_COLUMN)
  return tf.estimator.export.ServingInputReceiver(features, {'csv_row': csv_row})


def example_serving_input_fn():
  """Build the serving inputs."""
  example_bytestring = tf.placeholder(
      shape=[None],
      dtype=tf.string,
  )
  feature_scalars = tf.parse_example(
      example_bytestring,
      tf.feature_column.make_parse_example_spec(INPUT_COLUMNS)
  )
  return tf.estimator.export.ServingInputReceiver(
      features,
      {'example_proto': example_bytestring}
  )

# [START serving-function]
def json_serving_input_fn():
  """Build the serving inputs."""
  inputs = {}
  for feat in INPUT_COLUMNS:
    inputs[feat.name] = tf.placeholder(shape=[None], dtype=feat.dtype)
    
  return tf.estimator.export.ServingInputReceiver(inputs, inputs)
# [END serving-function]

SERVING_FUNCTIONS = {
    'JSON': json_serving_input_fn,
    'EXAMPLE': example_serving_input_fn,
    'CSV': csv_serving_input_fn
}


def parse_csv(rows_string_tensor):
  """Takes the string input tensor and returns a dict of rank-2 tensors."""

  # Takes a rank-1 tensor and converts it into rank-2 tensor
  # Example if the data is ['csv,line,1', 'csv,line,2', ..] to
  # [['csv,line,1'], ['csv,line,2']] which after parsing will result in a
  # tuple of tensors: [['csv'], ['csv']], [['line'], ['line']], [[1], [2]]
  row_columns = tf.expand_dims(rows_string_tensor, -1)
  columns = tf.decode_csv(row_columns, record_defaults=CSV_COLUMN_DEFAULTS)
  features = dict(zip(CSV_COLUMNS, columns))

  # Remove unused columns
  for col in UNUSED_COLUMNS:
    features.pop(col)
  return features


def input_fn(filenames,
                      num_epochs=None,
                      shuffle=True,
                      skip_header_lines=0,
                      batch_size=200):
  """Generates features and labels for training or evaluation.
  This uses the input pipeline based approach using file name queue
  to read data so that entire data is not loaded in memory.

  Args:
      filenames: [str] list of CSV files to read data from.
      num_epochs: int how many times through to read the data.
        If None will loop through data indefinitely
      shuffle: bool, whether or not to randomize the order of data.
        Controls randomization of both file order and line order within
        files.
      skip_header_lines: int set to non-zero in order to skip header lines
        in CSV files.
      batch_size: int First dimension size of the Tensors returned by
        input_fn
  Returns:
      A (features, indices) tuple where features is a dictionary of
        Tensors, and indices is a single Tensor of label indices.
  """
  filename_dataset = tf.data.Dataset.from_tensor_slices(filenames)
  if shuffle:
    # Process the files in a random order.
    filename_dataset = filename_dataset.shuffle(len(filenames))
    
  # For each filename, parse it into one element per line, and skip the header
  # if necessary.
  dataset = filename_dataset.flat_map(
      lambda filename: tf.data.TextLineDataset(filename).skip(skip_header_lines))
  
  dataset = dataset.map(parse_csv)
  if shuffle:
    dataset = dataset.shuffle(buffer_size=batch_size * 10)
  dataset = dataset.repeat(num_epochs)
  dataset = dataset.batch(batch_size)
  iterator = dataset.make_one_shot_iterator()
  features = iterator.get_next()
  return features, parse_label_column(features.pop(LABEL_COLUMN))
