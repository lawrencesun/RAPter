#ifndef RAPTER_ASSIGNMENTOPS_HPP
#define RAPTER_ASSIGNMENTOPS_HPP

#include "rapter/simpleTypes.h"
#include "rapter/io/inputParser.hpp"
//#include "rapter/processing/util.hpp"
//#include "rapter/util/containers.hpp"
#include <chrono> // random seed

namespace rapter
{

    // Usage: .../Release/bin/toGlobFit --subsample-primitives 0.1 --pop-limit 100 --prims segments.csv --cloud cloud.ply -a points_segments.csv --scale 0.005
    template < class _PrimitiveVectorT
             , class _PrimitiveMapT
             , class _PointContainerT
             , class _PclCloudT>
    int approxUnassignedWPlanes( int argc, char** argv )
    {
        using namespace rapter;

        typedef typename _PrimitiveMapT::mapped_type    InnerContainerT;
        typedef typename _PclCloudT::Ptr                PclPtrT;
        typedef typename InnerContainerT::value_type    PrimitiveT;
        typedef typename PrimitiveT::Scalar             Scalar;
        typedef typename _PointContainerT::PrimitiveT   PointPrimitiveT;

        //unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
        srand( time(NULL) );

        _PointContainerT    points;
        PclPtrT             pclCloud;
        _PrimitiveVectorT   primitivesVector;
        _PrimitiveMapT      primitives;
        struct MyParams { Scalar scale; } params;

        rapter::parseInput<InnerContainerT,_PclCloudT>( points, pclCloud, primitivesVector, primitives, params, argc, argv, /* readAssoc: */ true );
        int popLimit;
        if ( rapter::console::parse_argument( argc, argv, "--pop-limit", popLimit) < 0 )
            std::cout << "This will probably not work, unless you give a higher (3..10) pop-limit with --pop-limit k" << std::endl;

        std::cout << "usage: --unass-w-planes --pop-limit --prim --assoc --scale --cloud" << std::endl;

        // get plane point counts
        rapter::GidPidVectorMap populations;
        processing::getPopulations( populations, points );

        // get unassigned points
        std::set<PidT> unassignedPIds;
        for ( size_t pid = 0; pid != points.size(); ++pid )
        {
            const GidT gid( points[pid].getTag(PointPrimitiveT::TAGS::GID) );
            if (    (gid                   == PointPrimitive::LONG_VALUES::UNSET)
                 || (populations.find(gid) != populations.end() && populations[gid].size() < popLimit) )
                unassignedPIds.insert( pid );
        } //...for pids
        std::cout << "[" << __func__ << "]: " << "there are " << unassignedPIds.size() << "/" << points.size() << " unassigned or practically unassigned points\n";

        return EXIT_SUCCESS;
    } //...approxUnassigned

} //...ns rapter

#endif // GO_ASSIGNMENTOPS_HPP
