using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class car : MonoBehaviour
{
    [Header("Car Movement")]
    [SerializeField] Vector3 carScale;

    [Header("Wheel Settings")]
    [SerializeField] GameObject wheel;
    [SerializeField] List<Vector3> wheelPositions;
    [SerializeField] Vector3 wheelScale;

    [Header("Movement Interpolation")]
    [SerializeField] Vector3 startPosition;
    [SerializeField] Vector3 endPosition;

    Mesh mesh;
    Vector3[] verticesCar;
    Vector3[] newVerticesCar;

    List<GameObject> wheelObjects = new List<GameObject>();
    List<Mesh> meshWheel = new List<Mesh>();
    List<Vector3[]> verticesWheel = new List<Vector3[]>();
    List<Vector3[]> newVerticesWheel = new List<Vector3[]>();

    void Start(){
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        verticesCar = mesh.vertices;
        newVerticesCar = new Vector3[verticesCar.Length];
        
        // Create a new array to store the new vertices
        foreach (Vector3 wheelPosition in wheelPositions){
            // Copy the vertices to the new array
            GameObject wheel = Instantiate(this.wheel, new Vector3(0,0,0), Quaternion.identity);
            wheelObjects.Add(wheel);
            
        }
        for (int i = 0; i < wheelObjects.Count; i++){
            meshWheel.Add(wheelObjects[i].GetComponentInChildren<MeshFilter>().mesh);
            verticesWheel.Add(meshWheel[i].vertices);
            newVerticesWheel.Add(new Vector3[verticesWheel[i].Length]);
        }
        
    }

    Vector3 Newtarget(Vector3 startPos, Vector3 newPosition, float time){
        if (!this.endPosition.Equals(newPosition)){
            startPosition = startPos;
            endPosition = newPosition;
            time = Mathf.Clamp(time, 0.0f, 1.0f);

            Vector3 lerpPosition = Vector3.Lerp(startPosition, endPosition, time);
            return lerpPosition;
        }
        else{
            return newPosition;
    }

    }
    

    public void SetMovement(Vector3 startPos, Vector3 newPosition, float time){
        //Call the function to move the car
        Matrix4x4 MoveCar = this.MoveCar(Newtarget(startPos, newPosition, time));
        ApplyCarTransform(MoveCar);
        //Call the function to move the wheels
        for (int i = 0; i < wheelObjects.Count; i++)
        {
            Matrix4x4 wheelTransformMatrix = MoveWheels(MoveCar, i);
            ApplyWheelTransform(wheelTransformMatrix, i);
        }
    }

    Matrix4x4 MoveCar(Vector3 interpolation)
    {   //Create a matrix to move the car
        Matrix4x4 moveMatrix = HW_Transforms.TranslationMat(interpolation.x, interpolation.y, interpolation.z);
        Matrix4x4 scaleMatrix = HW_Transforms.ScaleMat(carScale.x, carScale.y, carScale.z);
        if (interpolation.z != 0)
        {   //Create a matrix to rotate the car
            float angle = Mathf.Atan2(endPosition.x - startPosition.x, endPosition.z - startPosition.z) * Mathf.Rad2Deg;
            Matrix4x4 rotateMatrix = HW_Transforms.RotateMat(angle, AXIS.Y);
            return moveMatrix * rotateMatrix * scaleMatrix;
        }
        else
        {
            return moveMatrix * scaleMatrix;
        }
    }

    Matrix4x4 MoveWheels(Matrix4x4 moveCar, int wheelPos)
    {   //Create the matrices to move and rotate the wheels
        Matrix4x4 scaleMatrix = HW_Transforms.ScaleMat(wheelScale.x, wheelScale.y, wheelScale.z);
        Matrix4x4 rotateMatrix = HW_Transforms.RotateMat(90 * Time.time, AXIS.X);
        Matrix4x4 moveMatrix = HW_Transforms.TranslationMat(wheelPositions[wheelPos].x, wheelPositions[wheelPos].y, wheelPositions[wheelPos].z);
        //Return the matrices multiplied
        return moveCar * moveMatrix * rotateMatrix * scaleMatrix;
    }


    void ApplyCarTransform(Matrix4x4 carTransformMatrix)
    {   //Apply the transformation to the car
        for (int i = 0; i < newVerticesCar.Length; i++)
        {
            //Create a vector to store the vertices
            Vector4 temp = new Vector4(verticesCar[i].x, verticesCar[i].y, verticesCar[i].z, 1);
            newVerticesCar[i] = carTransformMatrix * temp;
        }
        //Apply the transformation to the mesh of the car
        mesh.vertices = newVerticesCar;
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
    }

    void ApplyWheelTransform(Matrix4x4 moveWheels, int wheelPos)
    {   //Apply the transformation to the wheels
        for (int j = 0; j < newVerticesWheel[wheelPos].Length; j++)
        {
            //Create a vector to store the vertices
            Vector4 temp = new Vector4(verticesWheel[wheelPos][j].x, verticesWheel[wheelPos][j].y, verticesWheel[wheelPos][j].z, 1);
            newVerticesWheel[wheelPos][j] = moveWheels * temp;
        }
        //Apply the transformation to the mesh of the wheels
        meshWheel[wheelPos].vertices = newVerticesWheel[wheelPos];
        meshWheel[wheelPos].RecalculateNormals();
        meshWheel[wheelPos].RecalculateBounds();
    }

    public void DeleteCar(){
        foreach (GameObject wheel in wheelObjects){
            Destroy(wheel);
        }
        
        Destroy(this.gameObject);
    }
}







